from typing import Optional, List
from sqlmodel import Session, select
from datetime import date

from app.models.position import Position
from app.models.trade import Trade
from app.schemas.position import PositionResponse


class PositionService:
    """持仓服务"""

    @staticmethod
    def get_all(session: Session) -> List[Position]:
        """获取所有持仓"""
        return session.exec(select(Position)).all()

    @staticmethod
    def get_active(session: Session) -> List[Position]:
        """获取活跃持仓"""
        return session.exec(
            select(Position).where(Position.status == "open")
        ).all()

    @staticmethod
    def get_by_id(session: Session, position_id: int) -> Optional[Position]:
        """根据ID获取持仓"""
        return session.exec(
            select(Position).where(Position.id == position_id)
        ).first()

    @staticmethod
    def get_by_stock(session: Session, stock_code: str) -> List[Position]:
        """获取指定股票的持仓"""
        return session.exec(
            select(Position).where(Position.stock_code == stock_code)
        ).all()

    @staticmethod
    def get_by_strategy(session: Session, strategy_id: int) -> List[Position]:
        """获取指定策略的持仓"""
        return session.exec(
            select(Position).where(Position.strategy_id == strategy_id)
        ).all()

    @staticmethod
    def calculate_total_value(session: Session) -> float:
        """计算总持仓市值"""
        positions = PositionService.get_active(session)
        return sum(p.market_value or 0 for p in positions)

    @staticmethod
    def calculate_total_pnl(session: Session) -> float:
        """计算总盈亏"""
        positions = PositionService.get_active(session)
        return sum(p.pnl or 0 for p in positions)

    @staticmethod
    def calculate_metrics(position: Position) -> dict:
        """计算持仓的市值、盈亏等指标"""
        current_price = position.current_price if position.current_price and position.current_price > 0 else position.avg_cost
        market_value = position.quantity * current_price
        profit_loss = (current_price - position.avg_cost) * position.quantity
        profit_ratio = ((current_price - position.avg_cost) / position.avg_cost * 100) if position.avg_cost > 0 else 0
        return {
            'current_price': current_price,
            'market_value': market_value,
            'profit_loss': profit_loss,
            'profit_ratio': profit_ratio,
        }

    @staticmethod
    def to_response(position: Position) -> PositionResponse:
        """将Position模型转换为API响应"""
        metrics = PositionService.calculate_metrics(position)
        return PositionResponse(
            stock_code=position.code,
            stock_name=position.name,
            quantity=position.quantity,
            available_quantity=position.quantity,
            cost_price=position.avg_cost,
            current_price=metrics['current_price'],
            market_value=metrics['market_value'],
            profit_amount=metrics['profit_loss'],
            profit_ratio=metrics['profit_ratio'],
            status=position.status,
            opened_at=position.entry_date,
            id=position.id,
            created_at=position.created_at,
            updated_at=position.updated_at,
            sell_target=position.sell_target,
            stop_loss=position.stop_loss,
            trade_plan=position.trade_plan,
            holding_reason=position.holding_reason,
        )

    @staticmethod
    def create_trade(db: Session, position: Position, action: str, price: float) -> Trade:
        """根据持仓创建交易记录"""
        trade = Trade(
            code=position.code,
            name=position.name,
            action=action,
            price=price,
            quantity=position.quantity,
            amount=price * position.quantity,
            fee=0,
            reason=f'{"建仓" if action == "买入" else "平仓"}: {position.name}',
            trade_date=date.today(),
        )
        if action == "卖出":
            trade.pnl = (price - position.avg_cost) * position.quantity
        db.add(trade)
        db.commit()
        db.refresh(trade)
        return trade
