from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
from sqlmodel import Session, select
from app.models.external_data import StockKline, StockBasic


class BacktestEngine:
    """回测引擎"""

    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions: Dict[str, Dict] = {}
        self.trades: List[Dict] = []
        self.equity_curve: List[Dict] = []

    def reset(self):
        """重置回测状态"""
        self.current_capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []

    def buy(
        self,
        stock_code: str,
        price: float,
        quantity: int,
        date: date
    ):
        """买入"""
        cost = price * quantity
        if cost > self.current_capital:
            return False

        self.current_capital -= cost

        if stock_code in self.positions:
            existing = self.positions[stock_code]
            total_quantity = existing["quantity"] + quantity
            avg_price = (
                existing["cost"] + cost
            ) / total_quantity
            self.positions[stock_code] = {
                "quantity": total_quantity,
                "avg_price": avg_price,
                "cost": existing["cost"] + cost,
            }
        else:
            self.positions[stock_code] = {
                "quantity": quantity,
                "avg_price": price,
                "cost": cost,
            }

        self.trades.append({
            "date": date,
            "stock_code": stock_code,
            "type": "buy",
            "price": price,
            "quantity": quantity,
            "cost": cost,
        })
        return True

    def sell(
        self,
        stock_code: str,
        price: float,
        quantity: int,
        date: date
    ):
        """卖出"""
        if stock_code not in self.positions:
            return False

        position = self.positions[stock_code]
        if position["quantity"] < quantity:
            return False

        revenue = price * quantity
        self.current_capital += revenue

        cost = position["avg_price"] * quantity
        pnl = revenue - cost

        position["quantity"] -= quantity
        if position["quantity"] == 0:
            del self.positions[stock_code]

        self.trades.append({
            "date": date,
            "stock_code": stock_code,
            "type": "sell",
            "price": price,
            "quantity": quantity,
            "revenue": revenue,
            "cost": cost,
            "pnl": pnl,
        })
        return True

    def get_portfolio_value(self, market_prices: Dict[str, float]) -> float:
        """计算组合市值"""
        positions_value = sum(
            market_prices.get(code, pos["avg_price"]) * pos["quantity"]
            for code, pos in self.positions.items()
        )
        return self.current_capital + positions_value

    def get_results(self) -> Dict:
        """获取回测结果"""
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.get("pnl", 0) > 0]
        losing_trades = [t for t in self.trades if t.get("pnl", 0) < 0]

        total_pnl = sum(t.get("pnl", 0) for t in self.trades)
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0

        final_value = self.get_portfolio_value(
            {code: pos["avg_price"] for code, pos in self.positions.items()}
        )
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100

        return {
            "initial_capital": self.initial_capital,
            "final_value": final_value,
            "total_return": total_return,
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate * 100,
            "total_pnl": total_pnl,
        }


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
