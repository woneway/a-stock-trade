from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date, datetime, timedelta
from typing import Optional, List
import time
import logging
import random

from app.database import engine
from app.models.stock import Stock
from app.models.external_data import (
    StockBasic,
    StockQuote,
    StockKline,
    SectorData,
    DragonListData,
    LimitData,
    CapitalFlowData,
    NorthMoneyData,
    SyncLog,
)
from app.models.market import (
    MarketIndex,
    LimitUpData,
    DragonListItem,
    CapitalFlow,
    SectorStrength,
    TurnoverRank,
)

logger = logging.getLogger(__name__)


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/sync", tags=["data-sync"])


def fetch_with_retry(func, max_retries=3, delay=2):
    """带重试的获取数据"""
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i < max_retries - 1:
                logger.warning(f"获取数据失败，{delay}秒后重试: {e}")
                time.sleep(delay)
            else:
                raise e


@router.post("/stocks")
def sync_stocks(db: Session = Depends(get_db)):
    """同步股票列表"""
    try:
        import akshare as ak
        stock_info_a_code_name_df = fetch_with_retry(lambda: ak.stock_info_a_code_name())
        stocks_added = 0
        
        for _, row in stock_info_a_code_name_df.iterrows():
            code = row.get("code", "")
            name = row.get("name", "")
            
            if not code or not name:
                continue
            
            existing = db.exec(select(Stock).where(Stock.code == code)).first()
            if existing:
                continue
            
            db_stock = Stock(code=code, name=name)
            db.add(db_stock)
            stocks_added += 1
        
        db.commit()
        return {"status": "success", "stocks_added": stocks_added}
    except Exception as e:
        logger.error(f"同步股票列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quotes")
def sync_quotes(db: Session = Depends(get_db), trade_date: date = None):
    """同步实时行情"""
    if trade_date is None:
        trade_date = date.today()
    
    try:
        import akshare as ak
        
        def fetch_quotes():
            return ak.stock_zh_a_spot_em()
        
        df = fetch_with_retry(fetch_quotes)
        quotes_updated = 0
        
        for _, row in df.iterrows():
            code = str(row.get("代码", ""))
            name = row.get("名称", "")
            price = row.get("最新价")
            change = row.get("涨跌幅")
            turnover_rate = row.get("换手率")
            volume_ratio = row.get("量比")
            amplitude = row.get("振幅")
            sector = row.get("所属行业", "")
            
            if not code:
                continue
            
            stock = db.exec(select(Stock).where(Stock.code == code)).first()
            if not stock:
                stock = Stock(code=code, name=name)
                db.add(stock)
            
            if price and price != "-":
                stock.price = float(price)
            if change and change != "-":
                stock.change = float(change)
            if turnover_rate and turnover_rate != "-":
                stock.turnover_rate = float(turnover_rate)
            if volume_ratio and volume_ratio != "-":
                stock.volume_ratio = float(volume_ratio)
            if amplitude and amplitude != "-":
                stock.amplitude = float(amplitude)
            if sector:
                stock.sector = sector
            stock.trade_date = trade_date
            stock.updated_at = datetime.now()
            
            quotes_updated += 1
        
        db.commit()
        return {"status": "success", "quotes_updated": quotes_updated}
    except Exception as e:
        logger.error(f"同步行情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quotes/baostock")
def sync_quotes_baostock(db: Session = Depends(get_db), trade_date: date = None):
    """使用baostock同步股票列表和行情"""
    if trade_date is None:
        trade_date = date.today()
    
    try:
        import baostock as bs
        
        lg = bs.login()
        if lg.error_code != '0':
            raise Exception(f"baostock登录失败: {lg.error_msg}")
        
        # 先获取股票列表
        rs = bs.query_stock_basic()
        
        stock_codes = []
        quotes_updated = 0
        stock_count = 0
        
        while rs.error_code == '0' and rs.next():
            data = rs.get_row_data()
            if len(data) < 6:
                continue
            
            code_full = data[0]
            name = data[1]
            stock_type = data[4]
            status = data[5]
            
            # 只获取正常交易的A股
            if status != '1':
                continue
            
            if not (code_full.startswith('sh.6') or code_full.startswith('sz.00') or code_full.startswith('sz.30')):
                continue
            
            code = code_full.split('.')[1]
            stock_count += 1
            
            if not code or not name:
                continue
            
            # 从 baostock code_full 前缀获取市场信息
            if code_full.startswith('sh.'):
                market = 'sh'
            elif code_full.startswith('sz.'):
                market = 'sz'
            else:
                market = None
            
            # 查找或创建股票
            stock = db.exec(select(Stock).where(Stock.code == code)).first()
            if not stock:
                stock = Stock(code=code, name=name, market=market)
                db.add(stock)
            else:
                stock.market = market
            
            # 先只保存基本信息，行情数据后面再获取
            stock.updated_at = datetime.now()
            
            if stock_count % 500 == 0:
                db.commit()
                logger.info(f"已处理 {stock_count} 只股票")
        
        db.commit()
        bs.logout()
        
        return {"status": "success", "quotes_updated": stock_count, "message": "股票列表同步完成"}
    except Exception as e:
        logger.error(f"使用baostock同步股票列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quotes/baostock-popular")
def sync_quotes_baostock_popular(db: Session = Depends(get_db), trade_date: date = None):
    """使用baostock同步热门股票行情"""
    if trade_date is None:
        trade_date = date.today()
    
    try:
        import baostock as bs
        
        lg = bs.login()
        if lg.error_code != '0':
            raise Exception(f"baostock登录失败: {lg.error_msg}")
        
        # 热门股票列表
        popular_codes = [
            ('600519', '贵州茅台'), ('600036', '招商银行'), ('000001', '平安银行'),
            ('600000', '浦发银行'), ('000858', '五粮液'), ('600030', '中信证券'),
            ('300750', '宁德时代'), ('002594', '比亚迪'), ('601318', '中国平安'),
            ('600900', '长江电力'), ('000333', '美的集团'), ('000651', '格力电器'),
            ('601888', '中国中免'), ('600276', '恒瑞医药'), ('300059', '东方财富'),
            ('002371', '北方华创'), ('688981', '中芯国际'), ('688008', '澜起科技'),
            ('688111', '华兴源创'), ('300308', '中际旭创'), ('300502', '新易盛'),
            ('002475', '立讯精密'), ('002230', '科大讯飞'), ('002594', '比亚迪'),
        ]
        
        fields = "date,code,open,high,low,close,volume,amount,preclose"
        
        quotes_updated = 0
        
        for code, name in popular_codes:
            if code.startswith('6'):
                code_full = f"sh.{code}"
            else:
                code_full = f"sz.{code}"
            
            rs = bs.query_history_k_data_plus(
                code_full,
                fields,
                start_date=trade_date.strftime('%Y-%m-%d'),
                end_date=trade_date.strftime('%Y-%m-%d'),
                frequency="d",
                adjustflag="2"
            )
            
            if rs.error_code != '0':
                continue
            
            while rs.error_code == '0' and rs.next():
                data = rs.get_row_data()
                if len(data) < 9:
                    continue
                
                stock = db.exec(select(Stock).where(Stock.code == code)).first()
                if not stock:
                    stock = Stock(code=code, name=name)
                    db.add(stock)
                
                try:
                    if data[5] and data[5] != '':
                        stock.price = float(data[5])
                    if data[8] and data[8] != '':
                        preclose = float(data[8])
                        if stock.price and preclose:
                            stock.change = round(((stock.price - preclose) / preclose) * 100, 2)
                    stock.trade_date = trade_date
                    stock.updated_at = datetime.now()
                    quotes_updated += 1
                except Exception as e:
                    logger.warning(f"处理数据失败: {e}")
                    continue
        
        bs.logout()
        db.commit()
        
        return {"status": "success", "quotes_updated": quotes_updated}
    except Exception as e:
        logger.error(f"使用baostock同步热门股票行情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quotes/baostock-full")
def sync_quotes_baostock_full(db: Session = Depends(get_db), trade_date: date = None, limit: int = 50):
    """使用baostock同步完整行情（包括价格、涨跌幅等）"""
    if trade_date is None:
        trade_date = date.today()
    
    try:
        import baostock as bs
        
        lg = bs.login()
        if lg.error_code != '0':
            raise Exception(f"baostock登录失败: {lg.error_msg}")
        
        # 获取股票代码
        stocks = db.exec(select(Stock).limit(limit)).all()
        
        if not stocks:
            return {"status": "success", "quotes_updated": 0, "message": "数据库中无股票"}
        
        fields = "date,code,open,high,low,close,volume,amount,preclose"
        
        quotes_updated = 0
        
        for stock in stocks:
            code = stock.code
            
            # 根据代码前缀确定交易所
            if code.startswith('6'):
                code_full = f"sh.{code}"
            elif code.startswith(('0', '3')):
                code_full = f"sz.{code}"
            else:
                continue
            
            rs = bs.query_history_k_data_plus(
                code_full,
                fields,
                start_date=trade_date.strftime('%Y-%m-%d'),
                end_date=trade_date.strftime('%Y-%m-%d'),
                frequency="d",
                adjustflag="2"
            )
            
            if rs.error_code != '0':
                continue
            
            while rs.error_code == '0' and rs.next():
                data = rs.get_row_data()
                if len(data) < 9:
                    continue
                
                try:
                    if data[5] and data[5] != '':
                        stock.price = float(data[5])
                    if data[8] and data[8] != '':
                        preclose = float(data[8])
                        if stock.price and preclose:
                            stock.change = round(((stock.price - preclose) / preclose) * 100, 2)
                    stock.trade_date = trade_date
                    stock.updated_at = datetime.now()
                    quotes_updated += 1
                except Exception as e:
                    logger.warning(f"处理数据失败: {e}")
                    continue
        
        bs.logout()
        db.commit()
        
        return {"status": "success", "quotes_updated": quotes_updated}
    except Exception as e:
        logger.error(f"使用baostock同步完整行情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/limit-up")
def sync_limit_up(db: Session = Depends(get_db), trade_date: date = None):
    """同步涨停数据"""
    if trade_date is None:
        trade_date = date.today()
    
    try:
        import akshare as ak
        
        def fetch_limit_up():
            return ak.stock_zh_a_limit_up_spot_em()
        
        df = fetch_with_retry(fetch_limit_up)
        
        total = len(df)
        new_high = 0
        if "龙虎榜" in df.columns:
            new_high = len(df[df.get("龙虎榜", "").str.contains("新晋", na=False)])
        
        limit_up = db.exec(
            select(LimitUpData).where(LimitUpData.trade_date == trade_date)
        ).first()
        
        if limit_up:
            limit_up.total = total
            limit_up.new_high = new_high
        else:
            limit_up = LimitUpData(
                trade_date=trade_date,
                total=total,
                yesterday=0,
                new_high=new_high,
                continuation=0
            )
            db.add(limit_up)
        
        for _, row in df.iterrows():
            code = str(row.get("代码", ""))
            
            stock = db.exec(select(Stock).where(Stock.code == code)).first()
            if stock:
                stock.is_limit_up = True
        
        db.commit()
        return {"status": "success", "total_limit_up": total}
    except Exception as e:
        logger.error(f"同步涨停数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sector-strength")
def sync_sector_strength(db: Session = Depends(get_db), trade_date: date = None):
    """同步板块强度"""
    if trade_date is None:
        trade_date = date.today()
    
    try:
        import akshare as ak
        
        def fetch_sector():
            return ak.stock_board_industry_name_em()
        
        df = fetch_with_retry(fetch_sector)
        
        for _, row in df.iterrows():
            name = row.get("板块名称", "")
            change = row.get("涨跌幅")
            up_count = row.get("上涨", 0)
            down_count = row.get("下跌", 0)
            
            sector = SectorStrength(
                name=name,
                strength=int(up_count) - int(down_count) if up_count and down_count else 0,
                trend="up" if (change and float(change) > 0) else "down",
                avg_change=float(change) if change else 0,
                trade_date=trade_date
            )
            db.add(sector)
        
        db.commit()
        return {"status": "success", "sectors_added": len(df)}
    except Exception as e:
        logger.error(f"同步板块强度失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/turnover-rank")
def sync_turnover_rank(db: Session = Depends(get_db), trade_date: date = None, limit: int = 50):
    """同步换手率排行榜"""
    if trade_date is None:
        trade_date = date.today()
    
    try:
        import akshare as ak
        
        def fetch_turnover():
            return ak.stock_zh_a_turnover_rate()
        
        df = fetch_with_retry(fetch_turnover)
        
        count = 0
        for _, row in df.head(limit).iterrows():
            code = str(row.get("代码", ""))
            name = row.get("名称", "")
            turnover_rate = row.get("换手率")
            price = row.get("最新价")
            change = row.get("涨跌幅")
            
            if not code or not name:
                continue
            
            rank = TurnoverRank(
                code=code,
                name=name,
                turnover_rate=float(turnover_rate) if turnover_rate else 0,
                amount=0,
                change=float(change) if change else 0,
                trade_date=trade_date
            )
            db.add(rank)
            count += 1
        
        db.commit()
        return {"status": "success", "ranks_added": count}
    except Exception as e:
        logger.error(f"同步换手率排行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/market-index")
def sync_market_index(db: Session = Depends(get_db), trade_date: date = None):
    """同步大盘指数"""
    if trade_date is None:
        trade_date = date.today()
    
    try:
        import akshare as ak
        
        indices = [
            ("sh000001", "上证指数"),
            ("sz399001", "深证成指"),
            ("sz399006", "创业板指"),
            ("sh000300", "沪深300"),
            ("sh000688", "科创50")
        ]
        
        for code, name in indices:
            try:
                def fetch_index():
                    return ak.stock_zh_index_daily(symbol=code)
                
                df = fetch_with_retry(fetch_index)
                if df is not None and not df.empty:
                    latest = df.iloc[-1]
                    
                    index_data = db.exec(
                        select(MarketIndex).where(
                            MarketIndex.index_name == name,
                            MarketIndex.trade_date == trade_date
                        )
                    ).first()
                    
                    if not index_data:
                        index_data = MarketIndex(
                            index_name=name,
                            trade_date=trade_date,
                            points=0,
                            change=0,
                            support=0,
                            resistance=0
                        )
                    
                    index_data.points = float(latest.get("close", 0))
                    index_data.change = float(latest.get("close", 0)) - float(latest.get("open", 0))
                    
                    db.add(index_data)
            except Exception as e:
                logger.warning(f"获取指数{code}失败: {e}")
                continue
        
        db.commit()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"同步大盘指数失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/demo")
def sync_demo_data(db: Session = Depends(get_db), trade_date: date = None):
    """同步演示数据（用于测试）"""
    if trade_date is None:
        trade_date = date.today()
    
    demo_stocks = [
        {"code": "000988", "name": "华工科技", "sector": "AI算力", "price": 35.5, "change": 5.2, "turnover_rate": 25.3, "volume_ratio": 2.1, "market_cap": 38, "limit_consecutive": 1},
        {"code": "000998", "name": "隆平高科", "sector": "AI算力", "price": 15.8, "change": 3.8, "turnover_rate": 18.5, "volume_ratio": 1.5, "market_cap": 25, "limit_consecutive": 0},
        {"code": "002371", "name": "北方华创", "sector": "半导体", "price": 285.6, "change": 8.5, "turnover_rate": 35.2, "volume_ratio": 3.2, "market_cap": 150, "limit_consecutive": 2},
        {"code": "688981", "name": "中芯国际", "sector": "半导体", "price": 42.3, "change": 6.8, "turnover_rate": 28.9, "volume_ratio": 2.8, "market_cap": 180, "limit_consecutive": 1},
        {"code": "002594", "name": "比亚迪", "sector": "新能源车", "price": 268.5, "change": 4.2, "turnover_rate": 15.6, "volume_ratio": 1.8, "market_cap": 780, "limit_consecutive": 0},
        {"code": "300750", "name": "宁德时代", "sector": "新能源车", "price": 182.3, "change": 3.5, "turnover_rate": 12.8, "volume_ratio": 1.4, "market_cap": 420, "limit_consecutive": 0},
        {"code": "300308", "name": "中际旭创", "sector": "光模块", "price": 125.6, "change": 9.8, "turnover_rate": 42.5, "volume_ratio": 4.5, "market_cap": 95, "limit_consecutive": 2},
        {"code": "300502", "name": "新易盛", "sector": "光模块", "price": 68.9, "change": 7.2, "turnover_rate": 38.2, "volume_ratio": 3.8, "market_cap": 45, "limit_consecutive": 1},
        {"code": "600030", "name": "中信证券", "sector": "证券", "price": 22.5, "change": 1.2, "turnover_rate": 8.5, "volume_ratio": 1.1, "market_cap": 320, "limit_consecutive": 0},
        {"code": "300059", "name": "东方财富", "sector": "证券", "price": 18.6, "change": 2.5, "turnover_rate": 15.2, "volume_ratio": 1.6, "market_cap": 180, "limit_consecutive": 0},
    ]
    
    for s in demo_stocks:
        stock = db.exec(select(Stock).where(Stock.code == s["code"])).first()
        if not stock:
            stock = Stock(code=s["code"], name=s["name"])
            db.add(stock)
        
        stock.sector = s["sector"]
        stock.price = s["price"]
        stock.change = s["change"]
        stock.turnover_rate = s["turnover_rate"]
        stock.volume_ratio = s["volume_ratio"]
        stock.market_cap = s["market_cap"]
        stock.limit_consecutive = s["limit_consecutive"]
        stock.is_limit_up = s["limit_consecutive"] > 0
        stock.trade_date = trade_date
        stock.updated_at = datetime.now()
    
    limit_up = db.exec(select(LimitUpData).where(LimitUpData.trade_date == trade_date)).first()
    if not limit_up:
        limit_up = LimitUpData(trade_date=trade_date, total=3, yesterday=2, new_high=1, continuation=2)
        db.add(limit_up)
    
    db.commit()
    
    return {"status": "success", "message": "演示数据同步完成"}


@router.post("/full")
def sync_all(db: Session = Depends(get_db), trade_date: date = None):
    """同步所有数据"""
    if trade_date is None:
        trade_date = date.today()
    
    results = {}
    
    try:
        results["stocks"] = sync_stocks(db).__dict__
    except Exception as e:
        results["stocks"] = {"error": str(e)}
    
    try:
        results["quotes"] = sync_quotes(db, trade_date).__dict__
    except Exception as e:
        results["quotes"] = {"error": str(e)}
    
    try:
        results["limit_up"] = sync_limit_up(db, trade_date).__dict__
    except Exception as e:
        results["limit_up"] = {"error": str(e)}
    
    try:
        results["sector_strength"] = sync_sector_strength(db, trade_date).__dict__
    except Exception as e:
        results["sector_strength"] = {"error": str(e)}
    
    return {"status": "success", "results": results}


@router.get("/status")
def get_sync_status(db: Session = Depends(get_db)):
    """获取同步状态"""
    stock_count = len(db.exec(select(Stock)).all())

    return {
        "status": "ready",
        "stock_count": stock_count,
        "apis": [
            "POST /api/sync/stocks - 同步股票列表",
            "POST /api/sync/quotes - 同步实时行情(AkShare)",
            "POST /api/sync/quotes/baostock - 同步实时行情(baostock)",
            "POST /api/sync/limit-up - 同步涨停数据",
            "POST /api/sync/sector-strength - 同步板块强度",
            "POST /api/sync/turnover-rank - 同步换手率排行",
            "POST /api/sync/market-index - 同步大盘指数",
            "POST /api/sync/demo - 同步演示数据(用于测试)",
            "POST /api/sync/full - 同步所有数据",
        ]
    }


@router.post("/v2/basics")
def sync_stock_basics_v2(db: Session = Depends(get_db)):
    """同步股票基本信息到新表(stock_basics)"""
    try:
        import baostock as bs

        lg = bs.login()
        if lg.error_code != '0':
            raise Exception(f"baostock登录失败: {lg.error_msg}")

        rs = bs.query_stock_basic()

        stock_count = 0
        stocks_added = 0

        while rs.error_code == '0' and rs.next():
            data = rs.get_row_data()
            if len(data) < 6:
                continue

            code_full = data[0]
            name = data[1]
            stock_type = data[4]
            status = data[5]

            if status != '1':
                continue

            if not (code_full.startswith('sh.6') or code_full.startswith('sz.00') or code_full.startswith('sz.30')):
                continue

            code = code_full.split('.')[1]

            if not code or not name:
                continue

            if code_full.startswith('sh.'):
                market = 'sh'
                exchange = 'SSE'
            elif code_full.startswith('sz.'):
                market = 'sz'
                exchange = 'SZSE'
            else:
                continue

            existing = db.exec(select(StockBasic).where(StockBasic.code_full == code_full)).first()

            if existing:
                existing.name = name
                existing.market = market
                existing.exchange = exchange
            else:
                new_stock = StockBasic(
                    code=code,
                    code_full=code_full,
                    name=name,
                    market=market,
                    exchange=exchange,
                    list_status='L'
                )
                db.add(new_stock)
                stocks_added += 1

            stock_count += 1

            if stock_count % 500 == 0:
                db.commit()
                logger.info(f"已处理 {stock_count} 只股票")

        db.commit()
        bs.logout()

        return {"status": "success", "total": stock_count, "added": stocks_added}
    except Exception as e:
        logger.error(f"同步股票基本信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/v2/quotes")
def sync_stock_quotes_v2(db: Session = Depends(get_db), trade_date: date = None):
    """同步股票行情到新表(stock_quotes)"""
    if trade_date is None:
        trade_date = date.today()

    try:
        import baostock as bs

        lg = bs.login()
        if lg.error_code != '0':
            raise Exception(f"baostock登录失败: {lg.error_msg}")

        stocks = db.exec(select(StockBasic)).all()

        if not stocks:
            bs.logout()
            return {"status": "success", "quotes_updated": 0, "message": "数据库中无股票基本信息"}

        fields = "date,code,open,high,low,close,volume,amount,preclose,turn"

        quotes_updated = 0

        for stock in stocks:
            code_full = stock.code_full

            rs = bs.query_history_k_data_plus(
                code_full,
                fields,
                start_date=trade_date.strftime('%Y-%m-%d'),
                end_date=trade_date.strftime('%Y-%m-%d'),
                frequency="d",
                adjustflag="2"
            )

            if rs.error_code != '0':
                continue

            while rs.error_code == '0' and rs.next():
                data = rs.get_row_data()
                if len(data) < 10:
                    continue

                try:
                    close_price = float(data[5]) if data[5] and data[5] != '' else None
                    preclose_price = float(data[8]) if data[8] and data[8] != '' else None

                    if close_price and preclose_price:
                        change = round(close_price - preclose_price, 2)
                        pct_chg = round((change / preclose_price) * 100, 2)
                    else:
                        change = None
                        pct_chg = None

                    quote = StockQuote(
                        stock_id=stock.id,
                        trade_date=trade_date,
                        open=float(data[2]) if data[2] and data[2] != '' else None,
                        high=float(data[3]) if data[3] and data[3] != '' else None,
                        low=float(data[4]) if data[4] and data[4] != '' else None,
                        close=close_price,
                        volume=float(data[6]) if data[6] and data[6] != '' else None,
                        amount=float(data[7]) if data[7] and data[7] != '' else None,
                        change=change,
                        pct_chg=pct_chg,
                        turnover_rate=float(data[9]) if data[9] and data[9] != '' else None,
                    )
                    db.add(quote)
                    quotes_updated += 1
                except Exception as e:
                    logger.warning(f"处理数据失败: {e}")
                    continue

        bs.logout()
        db.commit()

        return {"status": "success", "quotes_updated": quotes_updated}
    except Exception as e:
        logger.error(f"同步股票行情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/v2/klines")
def sync_stock_klines_v2(
    db: Session = Depends(get_db),
    start_date: str = None,
    end_date: str = None,
    codes: str = None
):
    """同步股票K线数据到新表(stock_klines)用于回测"""
    try:
        import baostock as bs

        if start_date is None:
            start_date = (date.today() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = date.today().strftime('%Y-%m-%d')

        lg = bs.login()
        if lg.error_code != '0':
            raise Exception(f"baostock登录失败: {lg.error_msg}")

        if codes:
            code_list = [c.strip() for c in codes.split(',')]
            stocks = db.exec(select(StockBasic).where(StockBasic.code.in_(code_list))).all()
        else:
            stocks = db.exec(select(StockBasic).limit(100)).all()

        fields = "date,code,open,high,low,close,volume,amount,preclose,turn"

        klines_updated = 0

        for stock in stocks:
            code_full = stock.code_full

            rs = bs.query_history_k_data_plus(
                code_full,
                fields,
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="2"
            )

            if rs.error_code != '0':
                continue

            while rs.error_code == '0' and rs.next():
                data = rs.get_row_data()
                if len(data) < 10:
                    continue

                try:
                    close_price = float(data[5]) if data[5] and data[5] != '' else None
                    preclose_price = float(data[8]) if data[8] and data[8] != '' else None

                    if close_price and preclose_price:
                        change = round(close_price - preclose_price, 2)
                        pct_chg = round((change / preclose_price) * 100, 2)
                    else:
                        change = None
                        pct_chg = None

                    kline = StockKline(
                        stock_id=stock.id,
                        trade_date=datetime.strptime(data[0], '%Y-%m-%d').date(),
                        open=float(data[2]) if data[2] and data[2] != '' else None,
                        high=float(data[3]) if data[3] and data[3] != '' else None,
                        low=float(data[4]) if data[4] and data[4] != '' else None,
                        close=close_price,
                        volume=float(data[6]) if data[6] and data[6] != '' else None,
                        amount=float(data[7]) if data[7] and data[7] != '' else None,
                        change=change,
                        pct_chg=pct_chg,
                        turnover_rate=float(data[9]) if data[9] and data[9] != '' else None,
                    )
                    db.add(kline)
                    klines_updated += 1
                except Exception as e:
                    logger.warning(f"处理K线数据失败: {e}")
                    continue

            if klines_updated % 1000 == 0:
                db.commit()
                logger.info(f"已处理 {klines_updated} 条K线数据")

        bs.logout()
        db.commit()

        return {"status": "success", "klines_updated": klines_updated}
    except Exception as e:
        logger.error(f"同步K线数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/v2/status")
def get_sync_status_v2(db: Session = Depends(get_db)):
    """获取新表同步状态"""
    stock_basic_count = len(db.exec(select(StockBasic)).all())
    stock_quote_count = len(db.exec(select(StockQuote)).all())
    stock_kline_count = len(db.exec(select(StockKline)).all())

    return {
        "status": "ready",
        "stock_basic_count": stock_basic_count,
        "stock_quote_count": stock_quote_count,
        "stock_kline_count": stock_kline_count,
        "apis": [
            "POST /api/sync/v2/basics - 同步股票基本信息到stock_basics",
            "POST /api/sync/v2/quotes - 同步股票行情到stock_quotes",
            "POST /api/sync/v2/klines - 同步股票K线数据到stock_klines(用于回测)",
        ]
    }
