from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import create_db_and_tables
from app.routers import (
    market,
    watch_stock,
    trade,
    plan,
    settings,
    position,
    alert,
    strategy,
    dashboard,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    from sqlmodel import Session, select
    from app.models.strategy import Strategy
    from app.database import engine

    with Session(engine) as session:
        existing = session.exec(select(Strategy)).first()
        if not existing:
            default_strategies = [
                Strategy(
                    name="龙头战法",
                    description="追涨龙头股，高收益策略",
                    stock_selection_logic="当日板块涨幅第一，换手率>15%，市值<100亿",
                    entry_condition="板块启动时买入龙头股",
                    exit_condition="板块回落或跌破5日均线卖出",
                    stop_loss=6.0,
                    take_profit_1=7.0,
                    take_profit_2=15.0,
                    trailing_stop=5.0,
                    max_daily_loss=-5.0,
                    max_positions=3,
                    min_single_position=10.0,
                    max_single_position=25.0,
                    is_active=True,
                ),
                Strategy(
                    name="龙回头",
                    description="龙头股回调后的反弹机会",
                    stock_selection_logic="前期龙头股回调至10日均线附近",
                    entry_condition="企稳后买入",
                    exit_condition="反弹至前高卖出",
                    stop_loss=6.0,
                    take_profit_1=7.0,
                    take_profit_2=15.0,
                    trailing_stop=5.0,
                    max_daily_loss=-5.0,
                    max_positions=3,
                    min_single_position=10.0,
                    max_single_position=25.0,
                    is_active=True,
                ),
                Strategy(
                    name="尾盘战法",
                    description="尾盘买入，次日冲高卖出",
                    stock_selection_logic="14:30后涨幅3-5%，量价齐升",
                    entry_condition="14:30后企稳买入",
                    exit_condition="次日冲高卖出",
                    stop_loss=6.0,
                    take_profit_1=7.0,
                    take_profit_2=15.0,
                    trailing_stop=5.0,
                    max_daily_loss=-5.0,
                    max_positions=3,
                    min_single_position=10.0,
                    max_single_position=25.0,
                    is_active=True,
                ),
            ]
            for s in default_strategies:
                session.add(s)
            session.commit()

    yield


app = FastAPI(
    title="A-Stock Trade API",
    description="股票交易计划管理系统 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(market.router)
app.include_router(watch_stock.router)
app.include_router(watch_stock.router_alias)
app.include_router(trade.router)
app.include_router(plan.router)
app.include_router(settings.router)
app.include_router(position.router)
app.include_router(alert.router)
app.include_router(strategy.router)
app.include_router(dashboard.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
