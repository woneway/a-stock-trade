from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from app.database import get_db
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON

router = APIRouter()


class MonitoredStockCreate(BaseModel):
    stock_code: str
    stock_name: str
    monitor_type: str
    target_price: Optional[float] = None
    alert_enabled: bool = True


class MonitoredStockResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: str
    monitor_type: str
    target_price: Optional[float]
    current_price: Optional[float]
    alert_enabled: bool
    created_at: datetime


class PriceAlertResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: str
    alert_type: str
    target_price: Optional[float]
    current_price: Optional[float]
    triggered: bool
    triggered_at: Optional[datetime]
    created_at: datetime


from sqlalchemy import Table, MetaData
from app.database import Base, engine

metadata = MetaData()

monitored_stocks_table = Table('monitored_stocks', metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('stock_code', String(10), nullable=False),
    Column('stock_name', String(50), nullable=False),
    Column('monitor_type', String(20), nullable=False),
    Column('target_price', Float),
    Column('current_price', Float),
    Column('alert_enabled', Boolean, default=True),
    Column('created_at', DateTime, default=datetime.now),
    Column('updated_at', DateTime, default=datetime.now, onupdate=datetime.now)
)

price_alerts_table = Table('price_alerts', metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('stock_code', String(10), nullable=False),
    Column('stock_name', String(50), nullable=False),
    Column('alert_type', String(20), nullable=False),
    Column('target_price', Float),
    Column('current_price', Float),
    Column('triggered', Boolean, default=False),
    Column('triggered_at', DateTime),
    Column('created_at', DateTime, default=datetime.now)
)

metadata.create_all(bind=engine)


@router.get("/monitored-stocks", response_model=List[MonitoredStockResponse])
def get_monitored_stocks(db: Session = Depends(get_db)):
    results = db.execute("SELECT * FROM monitored_stocks ORDER BY created_at DESC").fetchall()
    return results


@router.post("/monitored-stocks", response_model=MonitoredStockResponse)
def add_monitored_stock(stock: MonitoredStockCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        "SELECT * FROM monitored_stocks WHERE stock_code = :stock_code AND monitor_type = :monitor_type",
        {"stock_code": stock.stock_code, "monitor_type": stock.monitor_type}
    ).fetchone()

    if existing:
        raise HTTPException(status_code=400, detail="该股票已在监控中")

    result = db.execute(
        """
        INSERT INTO monitored_stocks
        (stock_code, stock_name, monitor_type, target_price, alert_enabled)
        VALUES (:stock_code, :stock_name, :monitor_type, :target_price, :alert_enabled)
        """,
        {
            "stock_code": stock.stock_code,
            "stock_name": stock.stock_name,
            "monitor_type": stock.monitor_type,
            "target_price": stock.target_price,
            "alert_enabled": stock.alert_enabled
        }
    )
    db.commit()

    new_stock = db.execute(
        "SELECT * FROM monitored_stocks WHERE id = :id",
        {"id": result.lastrowid}
    ).fetchone()
    return new_stock


@router.delete("/monitored-stocks/{stock_id}")
def remove_monitored_stock(stock_id: int, db: Session = Depends(get_db)):
    existing = db.execute(
        "SELECT * FROM monitored_stocks WHERE id = :id",
        {"id": stock_id}
    ).fetchone()

    if not existing:
        raise HTTPException(status_code=404, detail="监控股票不存在")

    db.execute("DELETE FROM monitored_stocks WHERE id = :id", {"id": stock_id})
    db.commit()
    return {"message": "已移除监控"}


@router.get("/alerts", response_model=List[PriceAlertResponse])
def get_alerts(
    triggered: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = "SELECT * FROM price_alerts"
    if triggered is not None:
        query += f" WHERE triggered = {1 if triggered else 0}"
    query += " ORDER BY created_at DESC"

    results = db.execute(query).fetchall()
    return results


@router.post("/alerts", response_model=PriceAlertResponse)
def create_alert(
    stock_code: str,
    stock_name: str,
    alert_type: str,
    target_price: float,
    db: Session = Depends(get_db)
):
    result = db.execute(
        """
        INSERT INTO price_alerts
        (stock_code, stock_name, alert_type, target_price, triggered)
        VALUES (:stock_code, :stock_name, :alert_type, :target_price, 0)
        """,
        {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "alert_type": alert_type,
            "target_price": target_price
        }
    )
    db.commit()

    new_alert = db.execute(
        "SELECT * FROM price_alerts WHERE id = :id",
        {"id": result.lastrowid}
    ).fetchone()
    return new_alert


@router.post("/alerts/{alert_id}/trigger")
def trigger_alert(alert_id: int, current_price: float, db: Session = Depends(get_db)):
    existing = db.execute(
        "SELECT * FROM price_alerts WHERE id = :id",
        {"id": alert_id}
    ).fetchone()

    if not existing:
        raise HTTPException(status_code=404, detail="警报不存在")

    db.execute(
        """
        UPDATE price_alerts
        SET triggered = 1, triggered_at = NOW(), current_price = :current_price
        WHERE id = :id
        """,
        {"id": alert_id, "current_price": current_price}
    )
    db.commit()

    triggered = db.execute(
        "SELECT * FROM price_alerts WHERE id = :id",
        {"id": alert_id}
    ).fetchone()
    return triggered


@router.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    existing = db.execute(
        "SELECT * FROM price_alerts WHERE id = :id",
        {"id": alert_id}
    ).fetchone()

    if not existing:
        raise HTTPException(status_code=404, detail="警报不存在")

    db.execute("DELETE FROM price_alerts WHERE id = :id", {"id": alert_id})
    db.commit()
    return {"message": "警报已删除"}


@router.get("/price/{stock_code}")
def get_stock_price(stock_code: str, db: Session = Depends(get_db)):
    monitored = db.execute(
        "SELECT * FROM monitored_stocks WHERE stock_code = :stock_code",
        {"stock_code": stock_code}
    ).fetchone()

    if monitored and monitored.current_price:
        return {
            "stock_code": stock_code,
            "stock_name": monitored.stock_name,
            "price": monitored.current_price,
            "source": "local"
        }

    return {
        "stock_code": stock_code,
        "stock_name": None,
        "price": None,
        "source": "unknown",
        "message": "请添加监控后获取实时价格"
    }


@router.put("/monitored-stocks/{stock_id}/update-price")
def update_stock_price(
    stock_id: int,
    current_price: float,
    db: Session = Depends(get_db)
):
    monitored = db.execute(
        "SELECT * FROM monitored_stocks WHERE id = :id",
        {"id": stock_id}
    ).fetchone()

    if not monitored:
        raise HTTPException(status_code=404, detail="监控股票不存在")

    db.execute(
        """
        UPDATE monitored_stocks
        SET current_price = :current_price, updated_at = NOW()
        WHERE id = :id
        """,
        {"id": stock_id, "current_price": current_price}
    )
    db.commit()

    if monitored.target_price and monitored.alert_enabled:
        should_trigger = False
        if monitored.monitor_type == "price_above" and current_price >= monitored.target_price:
            should_trigger = True
        elif monitored.monitor_type == "price_below" and current_price <= monitored.target_price:
            should_trigger = True

        if should_trigger:
            existing_alert = db.execute(
                "SELECT * FROM price_alerts WHERE stock_code = :stock_code AND triggered = 0",
                {"stock_code": monitored.stock_code}
            ).fetchone()

            if not existing_alert:
                db.execute(
                    """
                    INSERT INTO price_alerts
                    (stock_code, stock_name, alert_type, target_price, current_price, triggered)
                    VALUES (:stock_code, :stock_name, :alert_type, :target_price, :current_price, 1)
                    """,
                    {
                        "stock_code": monitored.stock_code,
                        "stock_name": monitored.stock_name,
                        "alert_type": monitored.monitor_type,
                        "target_price": monitored.target_price,
                        "current_price": current_price
                    }
                )
                db.commit()

    updated = db.execute(
        "SELECT * FROM monitored_stocks WHERE id = :id",
        {"id": stock_id}
    ).fetchone()
    return updated
