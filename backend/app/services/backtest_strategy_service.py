"""
回测策略 Service
"""
import json
import re
from typing import Optional, List, Dict, Any
from datetime import date
from sqlmodel import Session, select

from app.database import engine
from app.models.backtest_strategy import BacktestStrategy


class BacktestStrategyService:
    """回测策略服务"""

    @staticmethod
    def list(
        strategy_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[BacktestStrategy]:
        """获取回测策略列表"""
        with Session(engine) as session:
            statement = select(BacktestStrategy).order_by(BacktestStrategy.created_at.desc())

            if strategy_type:
                statement = statement.where(BacktestStrategy.strategy_type == strategy_type)
            if is_active is not None:
                statement = statement.where(BacktestStrategy.is_active == is_active)

            strategies = session.exec(statement).all()

            # 解析 params_definition JSON
            result = []
            for s in strategies:
                s_dict = s.model_dump()
                try:
                    s_dict["params_definition"] = json.loads(s.params_definition or "[]")
                except:
                    s_dict["params_definition"] = []
                result.append(s_dict)

            return result

    @staticmethod
    def get(strategy_id: int) -> Optional[dict]:
        """获取单个策略详情"""
        with Session(engine) as session:
            item = session.get(BacktestStrategy, strategy_id)
            if not item:
                return None

            item_dict = item.model_dump()
            try:
                item_dict["params_definition"] = json.loads(item.params_definition or "[]")
            except:
                item_dict["params_definition"] = []
            return item_dict

    @staticmethod
    def create(
        name: str,
        description: Optional[str],
        code: str,
        strategy_type: str,
        params_definition: Optional[List[Dict[str, Any]]],
        is_builtin: bool,
        is_active: bool,
    ) -> dict:
        """创建新的回测策略"""
        # 验证代码语法
        if code:
            try:
                compile(code, "<string>", "exec")
            except SyntaxError as e:
                raise ValueError(f"代码语法错误: {str(e)}")

        # 如果没有提供参数定义，尝试从代码中解析
        params_def = params_definition
        if not params_def and code:
            params_def = BacktestStrategyService.parse_strategy_params(code)

        with Session(engine) as session:
            db_item = BacktestStrategy(
                name=name,
                description=description,
                code=code,
                strategy_type=strategy_type,
                params_definition=json.dumps(params_def or [], ensure_ascii=False),
                is_builtin=is_builtin,
                is_active=is_active,
            )

            session.add(db_item)
            session.commit()
            session.refresh(db_item)

            # 返回时解析 params_definition
            db_item_dict = db_item.model_dump()
            db_item_dict["params_definition"] = params_def or []
            return db_item_dict

    @staticmethod
    def update(strategy_id: int, **kwargs) -> Optional[dict]:
        """更新策略"""
        # 验证代码语法
        if kwargs.get('code'):
            try:
                compile(kwargs['code'], "<string>", "exec")
            except SyntaxError as e:
                raise ValueError(f"代码语法错误: {str(e)}")

        with Session(engine) as session:
            db_item = session.get(BacktestStrategy, strategy_id)
            if not db_item:
                return None

            # 处理 params_definition
            if "params_definition" in kwargs and kwargs["params_definition"]:
                kwargs["params_definition"] = json.dumps(kwargs["params_definition"], ensure_ascii=False)

            for key, value in kwargs.items():
                if value is not None and hasattr(db_item, key):
                    setattr(db_item, key, value)
            db_item.updated_at = date.today()

            session.add(db_item)
            session.commit()
            session.refresh(db_item)

            db_item_dict = db_item.model_dump()
            try:
                db_item_dict["params_definition"] = json.loads(db_item.params_definition or "[]")
            except:
                db_item_dict["params_definition"] = []
            return db_item_dict

    @staticmethod
    def delete(strategy_id: int) -> bool:
        """删除策略"""
        with Session(engine) as session:
            item = session.get(BacktestStrategy, strategy_id)
            if not item:
                return False

            # 不允许删除内置策略
            if item.is_builtin:
                raise ValueError("Cannot delete built-in strategies")

            session.delete(item)
            session.commit()
            return True

    @staticmethod
    def init_builtin_strategies() -> int:
        """初始化内置策略"""
        BUILTIN_STRATEGIES = [
            {
                "name": "双均线交叉",
                "description": "快速均线上穿慢速均线买入，下穿卖出",
                "code": '''from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd


class SmaCross(Strategy):
    """双均线交叉策略"""
    n1 = 10
    n2 = 20

    def init(self):
        self.sma1 = self.I(
            lambda x: pd.Series(x).rolling(self.n1).mean(),
            self.data.Close
        )
        self.sma2 = self.I(
            lambda x: pd.Series(x).rolling(self.n2).mean(),
            self.data.Close
        )

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()
''',
                "params_definition": [
                    {"name": "n1", "label": "短期周期", "default": 10, "min": 5, "max": 50, "type": "int"},
                    {"name": "n2", "label": "长期周期", "default": 20, "min": 10, "max": 200, "type": "int"},
                ],
            },
            {
                "name": "RSI超买超卖",
                "description": "RSI低于下界买入，高于上界卖出",
                "code": '''from backtesting import Strategy
import pandas as pd


class RsiStrategy(Strategy):
    """RSI超买超卖策略"""
    rsi_period = 14
    rsi_upper = 70
    rsi_lower = 30

    def init(self):
        def RSI(series, n):
            delta = series.diff()
            gain = delta.where(delta > 0, 0).rolling(n).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(n).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))

        self.rsi = self.I(
            lambda x: RSI(pd.Series(x), self.rsi_period),
            self.data.Close
        )

    def next(self):
        if not self.position:
            if self.rsi[-1] < self.rsi_lower:
                self.buy()
        else:
            if self.rsi[-1] > self.rsi_upper:
                self.position.close()
''',
                "params_definition": [
                    {"name": "rsi_period", "label": "RSI周期", "default": 14, "min": 5, "max": 30, "type": "int"},
                    {"name": "rsi_upper", "label": "超买阈值", "default": 70, "min": 50, "max": 90, "type": "int"},
                    {"name": "rsi_lower", "label": "超卖阈值", "default": 30, "min": 10, "max": 50, "type": "int"},
                ],
            },
            {
                "name": "MACD策略",
                "description": "MACD柱状图上穿0轴买入，下穿卖出",
                "code": '''from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np


class MacdStrategy(Strategy):
    """MACD策略"""
    period_fast = 12
    period_slow = 26
    signal = 9

    def init(self):
        def MACD(series, n_fast, n_slow, n_signal):
            ema_fast = series.ewm(span=n_fast, adjust=False).mean()
            ema_slow = series.ewm(span=n_slow, adjust=False).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=n_signal, adjust=False).mean()
            histogram = macd_line - signal_line
            return macd_line, signal_line, histogram

        macd, sig, hist = MACD(
            pd.Series(self.data.Close),
            self.period_fast, self.period_slow, self.signal
        )
        self.macd = self.I(lambda: macd)
        self.signal = self.I(lambda: sig)
        self.hist = self.I(lambda: hist)

    def next(self):
        if not self.position:
            if crossover(self.hist, 0):
                self.buy()
        else:
            if crossover(0, self.hist):
                self.position.close()
''',
                "params_definition": [
                    {"name": "period_fast", "label": "快线周期", "default": 12, "min": 5, "max": 30, "type": "int"},
                    {"name": "period_slow", "label": "慢线周期", "default": 26, "min": 15, "max": 50, "type": "int"},
                    {"name": "signal", "label": "信号线周期", "default": 9, "min": 5, "max": 20, "type": "int"},
                ],
            },
            {
                "name": "布林带策略",
                "description": "价格跌破下轨买入，突破上轨卖出",
                "code": '''from backtesting import Strategy
import pandas as pd


class BollingerStrategy(Strategy):
    """布林带策略"""
    bb_period = 20
    bb_std = 2.0

    def init(self):
        sma = pd.Series(self.data.Close).rolling(self.bb_period).mean()
        std = pd.Series(self.data.Close).rolling(self.bb_period).std()
        self.upper = self.I(lambda: sma + std * self.bb_std)
        self.lower = self.I(lambda: sma - std * self.bb_std)
        self.sma = self.I(lambda: sma)

    def next(self):
        if not self.position:
            if self.data.Close[-1] < self.lower[-1]:
                self.buy()
        else:
            if self.data.Close[-1] > self.upper[-1]:
                self.position.close()
''',
                "params_definition": [
                    {"name": "bb_period", "label": "布林带周期", "default": 20, "min": 10, "max": 50, "type": "int"},
                    {"name": "bb_std", "label": "标准差倍数", "default": 2.0, "min": 1.5, "max": 3.0, "step": 0.1, "type": "float"},
                ],
            },
        ]

        count = 0
        with Session(engine) as session:
            for s in BUILTIN_STRATEGIES:
                # 检查是否已存在
                existing = session.exec(
                    select(BacktestStrategy).where(
                        BacktestStrategy.name == s["name"],
                        BacktestStrategy.strategy_type == "builtin"
                    )
                ).first()

                if not existing:
                    db_item = BacktestStrategy(
                        name=s["name"],
                        description=s["description"],
                        code=s["code"],
                        strategy_type="builtin",
                        params_definition=json.dumps(s["params_definition"], ensure_ascii=False),
                        is_builtin=True,
                        is_active=True,
                    )
                    session.add(db_item)
                    count += 1

            if count > 0:
                session.commit()

        return count

    @staticmethod
    def parse_code_params(code: str) -> dict:
        """解析策略代码，提取参数定义"""
        try:
            params = BacktestStrategyService.parse_strategy_params(code)
            return {"params": params, "valid": True}
        except Exception as e:
            return {"params": [], "valid": False, "error": str(e)}

    @staticmethod
    def parse_strategy_params(code: str) -> List[Dict[str, Any]]:
        """从Python代码中解析策略参数"""
        params = []

        # 查找 class Strategy 定义
        class_match = re.search(r'class\s+(\w+)\s*\([^)]*Strategy[^)]*\)\s*:', code)
        if not class_match:
            return params

        # 提取类体内容
        class_start = class_match.end()
        class_body = code[class_start:]
        indent_level = len(class_match.group(0)) - len(class_match.group(0).lstrip())

        # 查找类结束位置
        lines = class_body.split('\n')
        body_lines = []
        for line in lines:
            if line.strip() and not line.startswith(' ' * (indent_level + 1)) and not line.strip().startswith('#'):
                if re.match(r'^class\s+', line) or re.match(r'^def\s+', line):
                    break
            body_lines.append(line)

        class_body = '\n'.join(body_lines)

        # 匹配类属性赋值
        prop_pattern = r'^(\s*)([a-z_][a-z0-9_]*)\s*=\s*(.+?)(?:\s*#.*)?$'

        for line in class_body.split('\n'):
            match = re.match(prop_pattern, line)
            if match:
                indent, name, value_str = match.groups()

                # 跳过方法定义
                if '(' in value_str:
                    continue

                # 解析默认值
                value_str = value_str.strip()
                default_value = None
                param_type = "int"

                try:
                    default_value = eval(value_str)
                except:
                    continue

                # 确定类型
                if isinstance(default_value, bool):
                    param_type = "bool"
                elif isinstance(default_value, int):
                    param_type = "int"
                elif isinstance(default_value, float):
                    param_type = "float"
                else:
                    continue

                # 设置合理的范围
                min_val, max_val = None, None
                if param_type == "int":
                    min_val = 1
                    max_val = 100
                    if "period" in name or "days" in name or "n" in name:
                        max_val = 200
                    elif "upper" in name or "lower" in name:
                        min_val = 0
                        max_val = 100
                elif param_type == "float":
                    min_val = 0.1
                    max_val = 10.0
                    if "std" in name:
                        max_val = 3.0

                params.append({
                    "name": name,
                    "label": name.replace('_', ' '),
                    "default": default_value,
                    "min": min_val,
                    "max": max_val,
                    "step": 1 if param_type == "int" else 0.1,
                    "type": param_type,
                })

        return params
