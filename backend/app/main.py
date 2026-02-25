from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    stock,
    strategy_scan,
    backtest,
    data_sync,
    external_data,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    from sqlmodel import Session, select
    from app.models.strategy import Strategy
    from app.models.stock import Stock
    from app.database import engine

    with Session(engine) as session:
        # 预设策略
        existing = session.exec(select(Strategy)).first()
        if not existing:
            default_strategies = [
                Strategy(
                    name="龙头战法",
                    description="追涨龙头股，高收益策略",
                    stock_selection_logic="当日板块涨幅第一，换手率>15%，市值<100亿",
                    watch_signals="龙头,连板,最高板",
                    entry_condition="板块启动时买入龙头股",
                    exit_condition="板块回落或跌破5日均线卖出",
                    min_turnover_rate=15,
                    max_turnover_rate=45,
                    min_market_cap=10,
                    max_market_cap=100,
                    limit_up_days=1,
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
                    watch_signals="低吸,回调,龙回头",
                    entry_condition="企稳后买入",
                    exit_condition="反弹至前高卖出",
                    min_turnover_rate=10,
                    max_turnover_rate=30,
                    min_market_cap=20,
                    max_market_cap=200,
                    limit_up_days=2,
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
                    watch_signals="尾盘,半路",
                    entry_condition="14:30后企稳买入",
                    exit_condition="次日冲高卖出",
                    min_turnover_rate=20,
                    max_turnover_rate=50,
                    min_market_cap=10,
                    max_market_cap=80,
                    limit_up_days=0,
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

        # 预设股票池
        stock_count = len(session.exec(select(Stock)).all())
        if stock_count == 0:
            default_stocks = [
                # AI/算力
                Stock(code="000988", name="华工科技", sector="AI算力", price=35.5, change=5.2, turnover_rate=25.3, volume_ratio=2.1, market_cap=38, limit_consecutive=1),
                Stock(code="000998", name="隆平高科", sector="AI算力", price=15.8, change=3.8, turnover_rate=18.5, volume_ratio=1.5, market_cap=25, limit_consecutive=0),
                Stock(code="002371", name="北方华创", sector="半导体", price=285.6, change=8.5, turnover_rate=35.2, volume_ratio=3.2, market_cap=150, limit_consecutive=2),
                Stock(code="688981", name="中芯国际", sector="半导体", price=42.3, change=6.8, turnover_rate=28.9, volume_ratio=2.8, market_cap=180, limit_consecutive=1),
                # 新能源车
                Stock(code="002594", name="比亚迪", sector="新能源车", price=268.5, change=4.2, turnover_rate=15.6, volume_ratio=1.8, market_cap=780, limit_consecutive=0),
                Stock(code="300750", name="宁德时代", sector="新能源车", price=182.3, change=3.5, turnover_rate=12.8, volume_ratio=1.4, market_cap=420, limit_consecutive=0),
                # 光模块
                Stock(code="300308", name="中际旭创", sector="光模块", price=125.6, change=9.8, turnover_rate=42.5, volume_ratio=4.5, market_cap=95, limit_consecutive=2),
                Stock(code="300502", name="新易盛", sector="光模块", price=68.9, change=7.2, turnover_rate=38.2, volume_ratio=3.8, market_cap=45, limit_consecutive=1),
                # 证券
                Stock(code="600030", name="中信证券", sector="证券", price=22.5, change=1.2, turnover_rate=8.5, volume_ratio=1.1, market_cap=320, limit_consecutive=0),
                Stock(code="300059", name="东方财富", sector="证券", price=18.6, change=2.5, turnover_rate=15.2, volume_ratio=1.6, market_cap=180, limit_consecutive=0),
                # 银行
                Stock(code="600036", name="招商银行", sector="银行", price=35.8, change=0.8, turnover_rate=3.5, volume_ratio=0.9, market_cap=890, limit_consecutive=0),
                Stock(code="000001", name="平安银行", sector="银行", price=12.3, change=0.5, turnover_rate=4.2, volume_ratio=0.8, market_cap=220, limit_consecutive=0),
                # 消费
                Stock(code="600519", name="贵州茅台", sector="消费", price=1680.5, change=1.5, turnover_rate=2.1, volume_ratio=0.8, market_cap=21000, limit_consecutive=0),
                Stock(code="000858", name="五粮液", sector="消费", price=158.6, change=2.1, turnover_rate=5.8, volume_ratio=1.2, market_cap=610, limit_consecutive=0),
                # 医药
                Stock(code="300760", name="迈瑞医疗", sector="医药", price=298.5, change=3.2, turnover_rate=8.5, volume_ratio=1.4, market_cap=360, limit_consecutive=0),
                Stock(code="000566", name="海南海药", sector="医药", price=8.5, change=-2.3, turnover_rate=22.5, volume_ratio=1.8, market_cap=15, limit_consecutive=0),
            ]
            for s in default_stocks:
                session.add(s)
            session.commit()

    yield


app = FastAPI(
    title="A-Stock Trade API",
    description="股票交易计划管理系统 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(stock.router)
app.include_router(strategy_scan.router)
app.include_router(backtest.router)
app.include_router(data_sync.router)
app.include_router(external_data.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
