from typing import List, Dict, Optional, Any
from datetime import date, datetime, timedelta
from sqlmodel import Session, select
import pandas as pd
from app.models.external_data import StockKline, StockBasic


class BacktestEngine:
    """基于backtesting.py的回测引擎"""

    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.results: Optional[Dict] = None

    def get_kline_dataframe(
        self,
        session: Session,
        stock_code: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """获取K线数据并转换为DataFrame"""
        stock = session.exec(
            select(StockBasic).where(StockBasic.code == stock_code)
        ).first()

        if not stock:
            return pd.DataFrame()

        klines = session.exec(
            select(StockKline).where(
                StockKline.stock_id == stock.id,
                StockKline.trade_date >= start_date,
                StockKline.trade_date <= end_date,
            ).order_by(StockKline.trade_date.asc())
        ).all()

        if not klines:
            return pd.DataFrame()

        data = []
        for k in klines:
            data.append({
                'Open': k.open or 0,
                'High': k.high or 0,
                'Low': k.low or 0,
                'Close': k.close or 0,
                'Volume': k.volume or 0,
            })

        df = pd.DataFrame(data)
        return df

    def run_ma_cross(
        self,
        df: pd.DataFrame,
        fast_period: int = 10,
        slow_period: int = 20
    ) -> Dict[str, Any]:
        """双均线交叉策略"""
        from backtesting import Backtest, Strategy
        from backtesting.lib import crossover

        class SmaCross(Strategy):
            n1 = fast_period
            n2 = slow_period

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

        bt = Backtest(
            df, SmaCross,
            cash=self.initial_capital,
            commission=0.001,
            exclusive_orders=True,
            finalize_trades=True
        )
        stats = bt.run()
        return self._format_stats(stats)

    def run_rsi(
        self,
        df: pd.DataFrame,
        period: int = 14,
        upper: int = 70,
        lower: int = 30
    ) -> Dict[str, Any]:
        """RSI超买超卖策略"""
        from backtesting import Backtest, Strategy
        from backtesting.lib import crossover

        def RSI(series, n):
            delta = series.diff()
            gain = delta.where(delta > 0, 0).rolling(n).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(n).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))

        class RsiStrategy(Strategy):
            rsi_period = period
            rsi_upper = upper
            rsi_lower = lower

            def init(self):
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

        bt = Backtest(
            df, RsiStrategy,
            cash=self.initial_capital,
            commission=0.001,
            exclusive_orders=True,
            finalize_trades=True
        )
        stats = bt.run()
        return self._format_stats(stats)

    def run_macd(
        self,
        df: pd.DataFrame,
        period_fast: int = 12,
        period_slow: int = 26,
        signal: int = 9
    ) -> Dict[str, Any]:
        """MACD策略"""
        from backtesting import Backtest, Strategy
        from backtesting.lib import crossover
        import numpy as np

        def MACD(series, n_fast, n_slow, n_signal):
            ema_fast = series.ewm(span=n_fast, adjust=False).mean()
            ema_slow = series.ewm(span=n_slow, adjust=False).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=n_signal, adjust=False).mean()
            histogram = macd_line - signal_line
            return macd_line, signal_line, histogram

        class MacdStrategy(Strategy):
            def init(self):
                macd, signal, hist = MACD(
                    pd.Series(self.data.Close),
                    period_fast, period_slow, signal
                )
                self.macd = self.I(lambda: macd)
                self.signal = self.I(lambda: signal)
                self.hist = self.I(lambda: hist)

            def next(self):
                if not self.position:
                    if crossover(self.hist, 0):
                        self.buy()
                else:
                    if crossover(0, self.hist):
                        self.position.close()

        bt = Backtest(
            df, MacdStrategy,
            cash=self.initial_capital,
            commission=0.001,
            exclusive_orders=True,
            finalize_trades=True
        )
        stats = bt.run()
        return self._format_stats(stats)

    def run_bollinger(
        self,
        df: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, Any]:
        """布林带策略"""
        from backtesting import Backtest, Strategy
        from backtesting.lib import crossover

        class BollingerStrategy(Strategy):
            bb_period = period
            bb_std = std_dev

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

        bt = Backtest(
            df, BollingerStrategy,
            cash=self.initial_capital,
            commission=0.001,
            exclusive_orders=True,
            finalize_trades=True
        )
        stats = bt.run()
        return self._format_stats(stats)

    def _format_stats(self, stats) -> Dict[str, Any]:
        """格式化回测结果"""
        import math
        import numpy as np
        
        def safe_float(val, default=0.0):
            if val is None:
                return default
            try:
                fval = float(val)
                if math.isnan(fval) or math.isinf(fval):
                    return default
                return fval
            except:
                return default

        result = {
            "initial_capital": safe_float(stats.get('Start Equity'), self.initial_capital),
            "final_value": safe_float(stats.get('End Equity'), 0),
            "total_return": safe_float(stats.get('Return (%)'), 0),
            "annual_return": safe_float(stats.get('Return (Ann.) (%)'), 0),
            "sharpe_ratio": safe_float(stats.get('Sharpe Ratio'), 0),
            "max_drawdown": safe_float(stats.get('Max. Drawdown (%)'), 0),
            "win_rate": safe_float(stats.get('Win Rate (%)'), 0),
            "total_trades": int(stats.get('# Trades', 0)),
            "best_trade": safe_float(stats.get('Best Trade (%)'), 0),
            "worst_trade": safe_float(stats.get('Worst Trade (%)'), 0),
            "avg_trade": safe_float(stats.get('Avg. Trade (%)'), 0),
        }
        
        # Convert all values to native Python floats to avoid numpy serialization issues
        return {k: float(v) if v is not None else 0 for k, v in result.items()}


def get_kline_data(
    session: Session,
    stock_code: str,
    start_date: str,
    end_date: str
) -> List[StockKline]:
    """获取K线数据"""
    stock = session.exec(
        select(StockBasic).where(StockBasic.code == stock_code)
    ).first()

    if not stock:
        return []

    return session.exec(
        select(StockKline).where(
            StockKline.stock_id == stock.id,
            StockKline.trade_date >= start_date,
            StockKline.trade_date <= end_date,
        ).order_by(StockKline.trade_date.asc())
    ).all()
