from typing import Optional, List
from datetime import date
from sqlmodel import Session, select, func
from app.models.trade import Trade
from app.schemas.trade import TradeResponse, TradeSummary


class TradeService:
    """交易服务"""

    @staticmethod
    def get_all(session: Session, limit: int = 100) -> List[Trade]:
        """获取所有交易记录"""
        return session.exec(select(Trade).limit(limit)).all()

    @staticmethod
    def get_by_id(session: Session, trade_id: int) -> Optional[Trade]:
        """根据ID获取交易记录"""
        return session.exec(select(Trade).where(Trade.id == trade_id)).first()

    @staticmethod
    def get_by_date(session: Session, trade_date: date) -> List[Trade]:
        """获取指定日期的交易记录"""
        return session.exec(
            select(Trade).where(Trade.trade_date == trade_date)
        ).all()

    @staticmethod
    def get_by_position(session: Session, position_id: int) -> List[Trade]:
        """获取指定持仓的交易记录"""
        return session.exec(
            select(Trade).where(Trade.position_id == position_id)
        ).all()

    @staticmethod
    def get_summary(session: Session) -> dict:
        """获取交易统计"""
        total_trades = session.exec(select(func.count(Trade.id))).first() or 0
        total_buy = session.exec(
            select(func.count(Trade.id)).where(Trade.trade_type == "buy")
        ).first() or 0
        total_sell = session.exec(
            select(func.count(Trade.id)).where(Trade.trade_type == "sell")
        ).first() or 0

        return {
            "total_trades": total_trades,
            "total_buy": total_buy,
            "total_sell": total_sell,
        }

    @staticmethod
    def calculate_pnl(session: Session, trade_date: date = None) -> float:
        """计算盈亏"""
        query = select(Trade)
        if trade_date:
            query = query.where(Trade.trade_date == trade_date)

        trades = session.exec(query).all()
        total_pnl = sum(t.pnl or 0 for t in trades)
        return total_pnl

    @staticmethod
    def convert_action(action: str) -> str:
        """转换动作类型为中文"""
        if action == "buy":
            return "买入"
        elif action == "sell":
            return "卖出"
        return action

    @staticmethod
    def convert_to_action(trade_type: str) -> str:
        """转换中文动作类型为英文"""
        if trade_type == "买入":
            return "buy"
        elif trade_type == "卖出":
            return "sell"
        return trade_type

    @staticmethod
    def to_response(trade: Trade) -> TradeResponse:
        """将Trade模型转换为API响应"""
        return TradeResponse(
            stock_code=trade.code,
            stock_name=trade.name,
            trade_type=TradeService.convert_action(trade.action),
            price=trade.price,
            quantity=trade.quantity,
            amount=trade.amount,
            fee=trade.fee,
            reason=trade.reason,
            trade_time=trade.trade_time,
            entry_price=trade.entry_price,
            exit_price=trade.exit_price,
            pnl=trade.pnl,
            pnl_percent=trade.pnl_percent,
            trade_date=trade.trade_date,
            id=trade.id,
            pre_plan_id=trade.pre_plan_id,
            is_planned=trade.is_planned,
            plan_target_price=trade.plan_target_price,
        )

    @staticmethod
    def calculate_summary(trades: List[Trade]) -> TradeSummary:
        """计算交易统计摘要"""
        total_trades = len(trades)
        buy_count = sum(1 for t in trades if t.action == "buy" or t.action == "买入")
        sell_count = sum(1 for t in trades if t.action == "sell" or t.action == "卖出")
        total_buy_amount = sum(t.amount for t in trades if t.action == "buy" or t.action == "买入")
        total_sell_amount = sum(t.amount for t in trades if t.action == "sell" or t.action == "卖出")
        total_fees = sum(t.fee for t in trades)
        net_profit = total_sell_amount - total_buy_amount - total_fees

        return TradeSummary(
            total_trades=total_trades,
            buy_count=buy_count,
            sell_count=sell_count,
            total_buy_amount=total_buy_amount,
            total_sell_amount=total_sell_amount,
            total_fees=total_fees,
            net_profit=net_profit,
        )
