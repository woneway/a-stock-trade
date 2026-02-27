from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import create_db_and_tables
from app.config import settings
from app.routers import daily
from app.routers.backtest_strategy import router as backtest_strategy_router
from app.routers import optimizer_enhanced
from app.routers import positions, trades
from app.routers import akshare
from app.routers import yz_board


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    # 启动时同步交易日历
    from datetime import datetime, timedelta
    import threading
    def sync_trade_calendar_background():
        try:
            from app.services.cache_service import CacheService

            # 获取最近一年的交易日历
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

            # 先尝试从本地获取
            local_data = CacheService._get_trade_calendar_from_local(start_date, end_date)
            if local_data and len(local_data) > 100:
                # 本地已有足够的交易日历数据
                return

            # 从 akshare 获取并保存
            df = CacheService._fetch_trade_calendar_from_akshare(start_date, end_date)
            if df is not None and not df.empty:
                CacheService._save_trade_calendar_to_local(df)
        except Exception as e:
            print(f"启动时同步交易日历失败: {e}")

    # 后台运行，不阻塞启动
    thread = threading.Thread(target=sync_trade_calendar_background)
    thread.daemon = True
    thread.start()

    yield


app = FastAPI(
    title="A-Stock Trade API",
    description="股票交易计划管理系统 API",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS 配置
allowed_origins = settings.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 核心功能
app.include_router(daily.router)                    # 计划与复盘
app.include_router(backtest_strategy_router)       # 自定义策略
app.include_router(optimizer_enhanced.router)       # 参数优化
app.include_router(akshare.router)                 # AKShare测试
app.include_router(yz_board.router)                # 游资看板

# 业务数据
app.include_router(positions.router)               # 持仓管理
app.include_router(trades.router)                  # 成交记录


@app.get("/health")
def health_check():
    return {"status": "ok"}
