from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import create_db_and_tables
from app.routers import daily
from app.routers.backtest import router as backtest_router
from app.routers.backtest import router_enhanced
from app.routers.backtest_strategy import router as backtest_strategy_router
from app.routers import optimizer_enhanced
from app.routers import data_v2


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="A-Stock Trade API",
    description="股票交易计划管理系统 API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 核心功能
app.include_router(daily.router)                    # 计划与复盘
app.include_router(backtest_router)               # 回测API
app.include_router(router_enhanced.router)         # 增强回测
app.include_router(backtest_strategy_router)       # 自定义策略
app.include_router(optimizer_enhanced.router)       # 参数优化
app.include_router(data_v2.router)                # 数据查询


@app.get("/health")
def health_check():
    return {"status": "ok"}
