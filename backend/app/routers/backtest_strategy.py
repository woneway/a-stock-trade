import json
import re
import inspect
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional, Any, Dict
from datetime import date
from pydantic import BaseModel

from app.database import engine
from app.models.backtest_strategy import BacktestStrategy
from app.schemas.backtest_strategy import (
    BacktestStrategyCreate,
    BacktestStrategyUpdate,
    BacktestStrategyResponse,
    StrategyParam,
)


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/backtest/strategies", tags=["backtest-strategies"])


@router.get("", response_model=List[BacktestStrategyResponse])
def get_strategies(
    db: Session = Depends(get_db),
    strategy_type: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """获取回测策略列表"""
    statement = select(BacktestStrategy).order_by(BacktestStrategy.created_at.desc())

    if strategy_type:
        statement = statement.where(BacktestStrategy.strategy_type == strategy_type)
    if is_active is not None:
        statement = statement.where(BacktestStrategy.is_active == is_active)

    strategies = db.exec(statement).all()

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


@router.post("", response_model=BacktestStrategyResponse)
def create_strategy(item: BacktestStrategyCreate, db: Session = Depends(get_db)):
    """创建新的回测策略"""
    # 验证代码语法
    if item.code:
        try:
            compile(item.code, "<string>", "exec")
        except SyntaxError as e:
            raise HTTPException(status_code=400, detail=f"代码语法错误: {str(e)}")

    # 如果没有提供参数定义，尝试从代码中解析
    params_def = item.params_definition
    if not params_def and item.code:
        params_def = parse_strategy_params(item.code)

    db_item = BacktestStrategy(
        name=item.name,
        description=item.description,
        code=item.code,
        strategy_type=item.strategy_type,
        params_definition=json.dumps(params_def or [], ensure_ascii=False),
        is_builtin=item.is_builtin,
        is_active=item.is_active,
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # 返回时解析 params_definition
    db_item_dict = db_item.model_dump()
    db_item_dict["params_definition"] = params_def or []
    return db_item_dict


@router.get("/{item_id}", response_model=BacktestStrategyResponse)
def get_strategy(item_id: int, db: Session = Depends(get_db)):
    """获取单个策略详情"""
    item = db.get(BacktestStrategy, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Strategy not found")

    item_dict = item.model_dump()
    try:
        item_dict["params_definition"] = json.loads(item.params_definition or "[]")
    except:
        item_dict["params_definition"] = []
    return item_dict


@router.put("/{item_id}", response_model=BacktestStrategyResponse)
def update_strategy(item_id: int, item: BacktestStrategyUpdate, db: Session = Depends(get_db)):
    """更新策略"""
    db_item = db.get(BacktestStrategy, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Strategy not found")

    # 验证代码语法
    if item.code:
        try:
            compile(item.code, "<string>", "exec")
        except SyntaxError as e:
            raise HTTPException(status_code=400, detail=f"代码语法错误: {str(e)}")

    item_data = item.model_dump(exclude_unset=True)

    # 处理 params_definition
    if "params_definition" in item_data and item_data["params_definition"]:
        item_data["params_definition"] = json.dumps(item_data["params_definition"], ensure_ascii=False)

    for key, value in item_data.items():
        setattr(db_item, key, value)
    db_item.updated_at = date.today()

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    db_item_dict = db_item.model_dump()
    try:
        db_item_dict["params_definition"] = json.loads(db_item.params_definition or "[]")
    except:
        db_item_dict["params_definition"] = []
    return db_item_dict


@router.delete("/{item_id}")
def delete_strategy(item_id: int, db: Session = Depends(get_db)):
    """删除策略"""
    item = db.get(BacktestStrategy, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Strategy not found")

    # 不允许删除内置策略
    if item.is_builtin:
        raise HTTPException(status_code=400, detail="Cannot delete built-in strategies")

    db.delete(item)
    db.commit()
    return {"ok": True}


class ParseCodeRequest(BaseModel):
    code: str


@router.post("/parse-params")
def parse_code_params(request: ParseCodeRequest):
    """解析策略代码，提取参数定义"""
    try:
        params = parse_strategy_params(request.code)
        return {"params": params, "valid": True}
    except Exception as e:
        return {"params": [], "valid": False, "error": str(e)}


def parse_strategy_params(code: str) -> List[Dict[str, Any]]:
    """从Python代码中解析策略参数

    查找符合 backtesting.py Strategy 规范的类属性定义
    支持的格式:
    - param_name = default_value  # 简单类型
    - param_name: type = default_value  # 带类型注解

    识别规则:
    - 类属性赋值 (在 class Strategy 内部)
    - 属性名为小写开头
    - 默认值为 int, float, bool 类型
    """
    params = []

    # 查找 class Strategy 定义
    class_match = re.search(r'class\s+(\w+)\s*\([^)]*Strategy[^)]*\)\s*:', code)
    if not class_match:
        return params

    class_name = class_match.group(1)

    # 提取类体内容
    class_start = class_match.end()
    # 简单提取：找到下一个同类级别的 class 或文件结束
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
    # 模式1: name = value (带注释)
    # 模式2: name: type = value

    # 查找所有属性赋值
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
                # 尝试解析为 Python 对象
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

            # 生成标签 (从下划线转中文)
            label = name.replace('_', ' ')

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
                "label": label,
                "default": default_value,
                "min": min_val,
                "max": max_val,
                "step": 1 if param_type == "int" else 0.1,
                "type": param_type,
            })

    return params


# 预设的内置策略
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


@router.get("/list", response_model=List[BacktestStrategyResponse])
def list_strategies(db: Session = Depends(get_db)):
    """获取自定义策略列表 (简化版)"""
    strategies = db.exec(
        select(BacktestStrategy).order_by(BacktestStrategy.created_at.desc())
    ).all()

    result = []
    for s in strategies:
        s_dict = s.model_dump()
        try:
            s_dict["params_definition"] = json.loads(s.params_definition or "[]")
        except:
            s_dict["params_definition"] = []
        result.append(s_dict)

    return result


@router.post("/init-builtin")
def init_builtin_strategies(db: Session = Depends(get_db)):
    """初始化内置策略"""
    count = 0
    for s in BUILTIN_STRATEGIES:
        # 检查是否已存在
        existing = db.exec(
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
            db.add(db_item)
            count += 1

    if count > 0:
        db.commit()

    return {"ok": True, "added": count}
