"""
回测引擎 Service
"""
from typing import Dict, Any, List
import pandas as pd
from app.services.data_service import DataService


class BacktestEngine:
    """增强的回测引擎，返回详细交易记录"""

    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.trades: List[Dict] = []
        self.equity_curve: List[Dict] = []

    def get_kline_dataframe(
        self,
        stock_code: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        return DataService.get_kline_dataframe(
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date
        )

    def run_ma_cross(
        self,
        df: pd.DataFrame,
        fast_period: int = 10,
        slow_period: int = 20
    ) -> Dict[str, Any]:
        """双均线交叉策略"""
        from backtesting import Backtest, Strategy
        from backtesting.lib import crossover

        self.trades = []
        self.equity_curve = []

        class SmaCross(Strategy):
            def init(self):
                self.sma1 = self.I(
                    lambda x: pd.Series(x).rolling(fast_period).mean(),
                    self.data.Close
                )
                self.sma2 = self.I(
                    lambda x: pd.Series(x).rolling(slow_period).mean(),
                    self.data.Close
                )

            def next(self):
                equity = self.equity
                self.equity_curve.append({
                    'date': self.data.index[-1] if hasattr(self.data, 'index') else len(self.equity_curve),
                    'equity': equity
                })

                if crossover(self.sma1, self.sma2):
                    if not self.position:
                        self.buy()
                        self.trades.append({
                            'type': 'buy',
                            'price': self.data.Close[-1],
                            'index': len(self.trades)
                        })
                elif crossover(self.sma2, self.sma1):
                    if self.position:
                        self.sell()
                        self.trades.append({
                            'type': 'sell',
                            'price': self.data.Close[-1],
                            'index': len(self.trades)
                        })

        bt = Backtest(
            df, SmaCross,
            cash=self.initial_capital,
            commission=0.001,
            exclusive_orders=True
        )
        stats = bt.run()

        result = self._format_stats(stats)
        result['trades'] = self._get_trade_records(stats)
        result['equity_curve'] = self._get_equity_curve(stats)
        result['indicators'] = self._calculate_indicators(df, fast_period, slow_period)
        return result

    def run_rsi(
        self,
        df: pd.DataFrame,
        period: int = 14,
        upper: int = 70,
        lower: int = 30
    ) -> Dict[str, Any]:
        """RSI超买超卖策略"""
        from backtesting import Backtest, Strategy

        def RSI(series, n):
            delta = series.diff()
            gain = delta.where(delta > 0, 0).rolling(n).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(n).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))

        self.trades = []
        self.equity_curve = []

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
                        self.trades.append({'type': 'buy', 'price': self.data.Close[-1]})
                else:
                    if self.rsi[-1] > self.rsi_upper:
                        self.position.close()
                        self.trades.append({'type': 'sell', 'price': self.data.Close[-1]})

        bt = Backtest(
            df, RsiStrategy,
            cash=self.initial_capital,
            commission=0.001,
            exclusive_orders=True
        )
        stats = bt.run()

        result = self._format_stats(stats)
        result['trades'] = self._get_trade_records(stats)
        result['equity_curve'] = self._get_equity_curve(stats)
        result['indicators'] = self._calculate_rsi_indicators(df, period)
        return result

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

        def MACD(series, n_fast, n_slow, n_signal):
            ema_fast = series.ewm(span=n_fast, adjust=False).mean()
            ema_slow = series.ewm(span=n_slow, adjust=False).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=n_signal, adjust=False).mean()
            histogram = macd_line - signal_line
            return macd_line, signal_line, histogram

        self.trades = []

        class MacdStrategy(Strategy):
            def init(self):
                macd, sig, hist = MACD(pd.Series(self.data.Close), period_fast, period_slow, signal)
                self.macd = self.I(lambda: macd)
                self.signal = self.I(lambda: sig)
                self.hist = self.I(lambda: hist)

            def next(self):
                if not self.position:
                    if crossover(self.hist, 0):
                        self.buy()
                        self.trades.append({'type': 'buy', 'price': self.data.Close[-1]})
                else:
                    if crossover(0, self.hist):
                        self.position.close()
                        self.trades.append({'type': 'sell', 'price': self.data.Close[-1]})

        bt = Backtest(
            df, MacdStrategy,
            cash=self.initial_capital,
            commission=0.001,
            exclusive_orders=True
        )
        stats = bt.run()

        result = self._format_stats(stats)
        result['trades'] = self._get_trade_records(stats)
        result['equity_curve'] = self._get_equity_curve(stats)
        result['indicators'] = self._calculate_macd_indicators(df, period_fast, period_slow, signal)
        return result

    def run_bollinger(
        self,
        df: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, Any]:
        """布林带策略"""
        from backtesting import Backtest, Strategy

        self.trades = []

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
                        self.trades.append({'type': 'buy', 'price': self.data.Close[-1]})
                else:
                    if self.data.Close[-1] > self.upper[-1]:
                        self.position.close()
                        self.trades.append({'type': 'sell', 'price': self.data.Close[-1]})

        bt = Backtest(
            df, BollingerStrategy,
            cash=self.initial_capital,
            commission=0.001,
            exclusive_orders=True
        )
        stats = bt.run()

        result = self._format_stats(stats)
        result['trades'] = self._get_trade_records(stats)
        result['equity_curve'] = self._get_equity_curve(stats)
        result['indicators'] = self._calculate_bb_indicators(df, period, std_dev)
        return result

    def run_simple_trend(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """简单趋势策略 - 阳线买入，阴线卖出"""
        from backtesting import Backtest, Strategy

        self.trades = []

        class SimpleTrendStrategy(Strategy):
            def init(self):
                pass

            def next(self):
                # 阳线买入
                if not self.position and self.data.Close[-1] > self.data.Open[-1]:
                    self.buy()
                    self.trades.append({'type': 'buy', 'price': self.data.Close[-1]})
                # 阴线卖出
                elif self.position and self.data.Close[-1] < self.data.Open[-1]:
                    self.position.close()
                    self.trades.append({'type': 'sell', 'price': self.data.Close[-1]})

        bt = Backtest(
            df, SimpleTrendStrategy,
            cash=self.initial_capital,
            commission=0.001,
            exclusive_orders=True
        )
        stats = bt.run()

        result = self._format_stats(stats)
        result['trades'] = self._get_trade_records(stats)
        result['equity_curve'] = self._get_equity_curve(stats)
        return result

    def run_stop_loss_profit(
        self,
        df: pd.DataFrame,
        stop_loss_pct: float = 10,
        stop_profit_pct: float = 10
    ) -> Dict[str, Any]:
        """止盈止损策略"""
        from backtesting import Backtest, Strategy

        self.trades = []
        self.equity_curve = []

        class StopLossProfitStrategy(Strategy):
            stop_loss = stop_loss_pct / 100
            stop_profit = stop_profit_pct / 100
            entry_price = 0

            def init(self):
                pass

            def next(self):
                if not self.position:
                    self.buy()
                    self.entry_price = self.data.Close[-1]
                    self.trades.append({
                        'type': 'buy',
                        'price': self.data.Close[-1],
                        'reason': '开仓'
                    })
                else:
                    pnl_pct = (self.data.Close[-1] - self.entry_price) / self.entry_price * 100

                    # 止损或止盈
                    if pnl_pct <= -self.stop_loss * 100 or pnl_pct >= self.stop_profit * 100:
                        self.position.close()
                        reason = '止盈' if pnl_pct >= self.stop_profit * 100 else '止损'
                        self.trades.append({
                            'type': 'sell',
                            'price': self.data.Close[-1],
                            'reason': reason,
                            'pnl_pct': pnl_pct
                        })

        bt = Backtest(
            df, StopLossProfitStrategy,
            cash=self.initial_capital,
            commission=0.001,
            exclusive_orders=True
        )
        stats = bt.run()

        result = self._format_stats(stats)
        result['trades'] = self._get_trade_records(stats)
        result['equity_curve'] = self._get_equity_curve(stats)
        return result

    def run_custom_strategy(
        self,
        df: pd.DataFrame,
        code: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """运行自定义策略"""
        from backtesting import Backtest, Strategy
        import sys
        from io import StringIO

        # 编译并执行策略代码
        try:
            compiled = compile(code, "<string>", "exec")
            local_ns = {}
            exec(compiled, local_ns)

            # 查找策略类
            StrategyClass = None
            for name, obj in local_ns.items():
                if isinstance(obj, type) and issubclass(obj, Strategy) and obj != Strategy:
                    StrategyClass = obj
                    break

            if not StrategyClass:
                return {"error": "未找到策略类"}

            # 设置策略参数
            for key, value in params.items():
                if hasattr(StrategyClass, key):
                    setattr(StrategyClass, key, value)

            bt = Backtest(
                df, StrategyClass,
                cash=self.initial_capital,
                commission=0.001,
                exclusive_orders=True
            )
            stats = bt.run()

            result = self._format_stats(stats)
            result['trades'] = self._get_trade_records(stats)
            result['equity_curve'] = self._get_equity_curve(stats)
            return result

        except Exception as e:
            return {"error": str(e)}

    def _format_stats(self, stats) -> Dict[str, Any]:
        import math

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

        return {
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

    def _get_trade_records(self, stats) -> List[Dict]:
        """获取交易记录"""
        trades = []
        if hasattr(stats, '_trades') and stats._trades is not None:
            df = stats._trades
            for idx, row in df.iterrows():
                trades.append({
                    'entry_time': str(idx[0]) if isinstance(idx, tuple) else str(idx),
                    'exit_time': str(idx[1]) if isinstance(idx, tuple) else '',
                    'entry_price': float(row.get('Entry Price', 0)),
                    'exit_price': float(row.get('Exit Price', 0)),
                    'size': int(row.get('Size', 0)),
                    'pnl': float(row.get('PNL', 0)),
                    'pnl_pct': float(row.get('Return (%)', 0)),
                })
        return trades

    def _get_equity_curve(self, stats) -> List[Dict]:
        """获取权益曲线"""
        if hasattr(stats, '_equity_curve') and stats._equity_curve is not None:
            return [
                {'equity': float(v), 'i': i}
                for i, v in enumerate(stats._equity_curve)
            ]
        return []

    def _calculate_indicators(self, df: pd.DataFrame, fast: int, slow: int) -> Dict:
        """计算均线指标"""
        close = df['Close']
        return {
            'ma_fast': close.rolling(fast).mean().fillna(0).tolist(),
            'ma_slow': close.rolling(slow).mean().fillna(0).tolist(),
            'close': close.tolist(),
        }

    def _calculate_rsi_indicators(self, df: pd.DataFrame, period: int) -> Dict:
        """计算RSI指标"""
        close = df['Close']
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return {
            'rsi': rsi.fillna(50).tolist(),
            'close': close.tolist(),
        }

    def _calculate_macd_indicators(self, df: pd.DataFrame, fast: int, slow: int, signal: int) -> Dict:
        """计算MACD指标"""
        close = df['Close']
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line

        return {
            'macd': macd.fillna(0).tolist(),
            'signal': signal_line.fillna(0).tolist(),
            'histogram': histogram.fillna(0).tolist(),
            'close': close.tolist(),
        }

    def _calculate_bb_indicators(self, df: pd.DataFrame, period: int, std_dev: float) -> Dict:
        """计算布林带指标"""
        close = df['Close']
        sma = close.rolling(period).mean()
        std = close.rolling(period).std()
        upper = sma + std * std_dev
        lower = sma - std * std_dev

        return {
            'upper': upper.fillna(0).tolist(),
            'lower': lower.fillna(0).tolist(),
            'sma': sma.fillna(0).tolist(),
            'close': close.tolist(),
        }
