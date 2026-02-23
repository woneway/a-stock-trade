from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional

from app.database import engine
from app.models.stock import Stock
from app.schemas.stock import StockCreate, StockUpdate, StockResponse, StockImport


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("", response_model=List[StockResponse])
def get_stocks(
    db: Session = Depends(get_db),
    sector: str = None,
    limit: int = 100,
    trade_date: str = None
):
    statement = select(Stock).order_by(Stock.id.desc())
    if sector:
        statement = statement.where(Stock.sector == sector)
    if trade_date:
        statement = statement.where(Stock.trade_date == trade_date)
    statement = statement.limit(limit)
    return db.exec(statement).all()


@router.get("/search", response_model=List[StockResponse])
def search_stocks(
    keyword: str,
    db: Session = Depends(get_db),
    limit: int = 10
):
    """搜索股票 by code or name"""
    statement = select(Stock).where(
        (Stock.code.contains(keyword)) | (Stock.name.contains(keyword))
    ).limit(limit)
    return db.exec(statement).all()


@router.get("/{stock_id}", response_model=StockResponse)
def get_stock(stock_id: int, db: Session = Depends(get_db)):
    stock = db.get(Stock, stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@router.post("", response_model=StockResponse)
def create_stock(item: StockCreate, db: Session = Depends(get_db)):
    # 检查是否已存在
    existing = db.exec(
        select(Stock).where(Stock.code == item.code)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Stock already exists")

    db_item = Stock.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.post("/import", response_model=List[StockResponse])
def import_stocks(item: StockImport, db: Session = Depends(get_db)):
    """批量导入股票"""
    results = []
    for stock_data in item.stocks:
        # 检查是否已存在
        existing = db.exec(
            select(Stock).where(Stock.code == stock_data.code)
        ).first()

        if existing:
            # 更新
            for key, value in stock_data.model_dump(exclude_unset=True).items():
                setattr(existing, key, value)
            db.add(existing)
            db.refresh(existing)
            results.append(existing)
        else:
            db_item = Stock.model_validate(stock_data)
            db.add(db_item)
            db.flush()
            results.append(db_item)

    db.commit()
    for item in results:
        db.refresh(item)
    return results


@router.put("/{stock_id}", response_model=StockResponse)
def update_stock(stock_id: int, item: StockUpdate, db: Session = Depends(get_db)):
    stock = db.get(Stock, stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(stock, key, value)

    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock


@router.delete("/{stock_id}")
def delete_stock(stock_id: int, db: Session = Depends(get_db)):
    stock = db.get(Stock, stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    db.delete(stock)
    db.commit()
    return {"ok": True}


@router.delete("")
def delete_all_stocks(db: Session = Depends(get_db)):
    """清空股票池"""
    db.exec(select(Stock))
    db.query(Stock).delete()
    db.commit()
    return {"ok": True, "message": "All stocks deleted"}
