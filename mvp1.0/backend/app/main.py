from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import plans, positions, trades, dashboard, review, monitor, settings
from app.database import engine, Base
from app.models.models import TradingPlan, Position, Trade, Account, RiskConfig, NotificationConfig, AppConfig

app = FastAPI(title="A股交易系统API", version="1.0.0")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(plans.router, prefix="/api/v1", tags=["交易计划"])
app.include_router(positions.router, prefix="/api/v1", tags=["持仓"])
app.include_router(trades.router, prefix="/api/v1", tags=["交易记录"])
app.include_router(review.router, prefix="/api/v1", tags=["复盘"])
app.include_router(monitor.router, prefix="/api/v1", tags=["监控"])
app.include_router(settings.router, prefix="/api/v1", tags=["设置"])

@app.get("/")
def root():
    return {"message": "A股交易系统API"}

@app.get("/health")
def health():
    return {"status": "ok"}
