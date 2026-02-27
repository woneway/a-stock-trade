"""
持仓 Service
"""
from typing import Optional, List, Any
from datetime import datetime, date
from sqlmodel import Session, select

from app.database import engine
from app.models.trading import Position


class PositionService:
    """持仓服务"""

    @staticmethod
    def list(
        stock_code: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Position]:
        """获取持仓列表"""
        with Session(engine) as session:
            query = select(Position)
            if stock_code:
                query = query.where(Position.stock_code == stock_code)
            if status:
                query = query.where(Position.status == status)
            query = query.order_by(Position.created_at.desc()).offset(offset).limit(limit)
            return session.exec(query).all()

    @staticmethod
    def get(position_id: int) -> Optional[Position]:
        """获取单个持仓"""
        with Session(engine) as session:
            return session.get(Position, position_id)

    @staticmethod
    def create(
        stock_code: str,
        stock_name: Optional[str],
        quantity: int,
        cost_price: float,
        current_price: Optional[float],
        stop_loss: Optional[float],
        take_profit: Optional[float],
        opened_at: date
    ) -> Position:
        """添加持仓"""
        with Session(engine) as session:
            db_position = Position(
                stock_code=stock_code,
                stock_name=stock_name,
                quantity=quantity,
                cost_price=cost_price,
                current_price=current_price or cost_price,
                available_quantity=quantity,
                stop_loss=stop_loss,
                take_profit=take_profit,
                opened_at=opened_at,
            )
            db_position.market_value = quantity * (current_price or cost_price)
            db_position.profit_amount = quantity * ((current_price or 0) - cost_price)
            if current_price and cost_price > 0:
                db_position.profit_ratio = (current_price - cost_price) / cost_price

            session.add(db_position)
            session.commit()
            session.refresh(db_position)
            return db_position

    @staticmethod
    def update(position_id: int, **kwargs) -> Optional[Position]:
        """更新持仓"""
        with Session(engine) as session:
            db_position = session.get(Position, position_id)
            if not db_position:
                return None

            for key, value in kwargs.items():
                if value is not None and hasattr(db_position, key):
                    setattr(db_position, key, value)

            db_position.updated_at = datetime.now()
            session.add(db_position)
            session.commit()
            session.refresh(db_position)
            return db_position

    @staticmethod
    def delete(position_id: int) -> bool:
        """删除持仓"""
        with Session(engine) as session:
            position = session.get(Position, position_id)
            if not position:
                return False
            session.delete(position)
            session.commit()
            return True

    @staticmethod
    def set_stop_loss(position_id: int, stop_loss: float) -> Optional[Position]:
        """设置止损"""
        return PositionService.update(position_id, stop_loss=stop_loss)

    @staticmethod
    def set_take_profit(position_id: int, take_profit: float) -> Optional[Position]:
        """设置止盈"""
        return PositionService.update(position_id, take_profit=take_profit)

    @staticmethod
    def close(position_id: int, close_price: float) -> Optional[Position]:
        """平仓"""
        with Session(engine) as session:
            position = session.get(Position, position_id)
            if not position:
                return None

            position.status = "sold"
            position.current_price = close_price
            position.profit_amount = position.quantity * (close_price - position.cost_price)
            if position.cost_price > 0:
                position.profit_ratio = (close_price - position.cost_price) / position.cost_price

            position.updated_at = datetime.now()
            session.add(position)
            session.commit()
            session.refresh(position)
            return position

    @staticmethod
    def summary() -> dict:
        """获取持仓汇总"""
        with Session(engine) as session:
            positions = session.exec(
                select(Position).where(Position.status == "holding")
            ).all()

            total_value = sum(p.quantity * p.current_price for p in positions)
            total_cost = sum(p.quantity * p.cost_price for p in positions)
            total_profit = total_value - total_cost
            profit_ratio = (total_profit / total_cost * 100) if total_cost > 0 else 0

            return {
                "total_positions": len(positions),
                "total_value": total_value,
                "total_cost": total_cost,
                "total_profit": total_profit,
                "profit_ratio": profit_ratio,
            }
