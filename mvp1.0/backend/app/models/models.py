from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class TradingPlan(Base):
    __tablename__ = "trading_plans"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), nullable=False)
    stock_name = Column(String(50), nullable=False)
    stock_type = Column(String(20), default="stock")
    trade_mode = Column(String(20), nullable=False)
    buy_timing = Column(String(50))
    validation_conditions = Column(JSON)
    target_price = Column(Float, nullable=False)
    position_ratio = Column(Float, nullable=False)
    stop_loss_price = Column(Float)
    stop_loss_ratio = Column(Float)
    take_profit_price = Column(Float)
    take_profit_ratio = Column(Float)
    hold_period = Column(String(20))
    logic = Column(Text)
    status = Column(String(20), default="observing")
    execute_result = Column(String(50))
    plan_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    positions = relationship("Position", back_populates="plan")
    trades = relationship("Trade", back_populates="plan")


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), nullable=False)
    stock_name = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    available_quantity = Column(Integer, nullable=False)
    cost_price = Column(Float, nullable=False)
    current_price = Column(Float)
    profit_amount = Column(Float)
    profit_ratio = Column(Float)
    stop_loss_price = Column(Float)
    take_profit_price = Column(Float)
    plan_id = Column(Integer, ForeignKey("trading_plans.id"))
    status = Column(String(20), default="holding")
    opened_at = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    plan = relationship("TradingPlan", back_populates="positions")
    trades = relationship("Trade", back_populates="position")


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), nullable=False)
    stock_name = Column(String(50), nullable=False)
    trade_type = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    fee = Column(Float, default=0)
    stamp_duty = Column(Float, default=0)
    position_id = Column(Integer, ForeignKey("positions.id"))
    plan_id = Column(Integer, ForeignKey("trading_plans.id"))
    trade_date = Column(Date, nullable=False)
    trade_time = Column(String(10))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    position = relationship("Position", back_populates="trades")
    plan = relationship("TradingPlan", back_populates="trades")


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    total_assets = Column(Float, default=100000)
    available_cash = Column(Float, default=100000)
    market_value = Column(Float, default=0)
    today_profit = Column(Float, default=0)
    today_profit_ratio = Column(Float, default=0)
    total_profit = Column(Float, default=0)
    total_profit_ratio = Column(Float, default=0)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class RiskConfig(Base):
    __tablename__ = "risk_config"

    id = Column(Integer, primary_key=True, index=True)
    max_position_ratio = Column(Float, default=20)
    daily_loss_limit = Column(Float, default=5)
    default_stop_loss = Column(Float, default=-5)
    default_take_profit = Column(Float, default=10)
    max_positions = Column(Integer, default=5)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class NotificationConfig(Base):
    __tablename__ = "notification_config"

    id = Column(Integer, primary_key=True, index=True)
    signal_notify = Column(Boolean, default=True)
    trade_notify = Column(Boolean, default=True)
    stop_loss_notify = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AppConfig(Base):
    __tablename__ = "app_config"

    id = Column(Integer, primary_key=True, index=True)
    theme = Column(String(20), default="light")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
