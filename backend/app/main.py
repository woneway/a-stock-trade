from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import create_db_and_tables
from app.routers import market, watch_stock, trade, plan


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="A-Stock Trade API",
    description="股票交易计划管理系统 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(market.router)
app.include_router(watch_stock.router)
app.include_router(trade.router)
app.include_router(plan.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
