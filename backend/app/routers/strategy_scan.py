from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel

from app.database import engine
from app.models.stock import Stock
from app.models.strategy import Strategy


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/strategy", tags=["strategy-scan"])


# ============ 响应模型 ============

class MatchDetail(BaseModel):
    field: str
    matched: bool
    detail: str
    score: int


class EntryAdvice(BaseModel):
    can_enter: bool
    signal: str
    risk: Optional[str] = None
    trigger_type: Optional[str] = None


class ExitAdvice(BaseModel):
    stop_loss: str
    take_profit_1: str
    take_profit_2: str
    trailing_stop: str
    advice: str


class ScanResult(BaseModel):
    stock_id: int
    code: str
    name: str
    sector: Optional[str] = None
    price: Optional[float] = None
    change: Optional[float] = None
    turnover_rate: Optional[float] = None
    volume_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    limit_consecutive: int = 0

    score: int
    max_score: int = 100
    match_details: List[MatchDetail]

    entry_advice: EntryAdvice
    exit_advice: ExitAdvice


class ScanResponse(BaseModel):
    strategy_id: int
    strategy_name: str
    results: List[ScanResult]


# ============ 权重配置 ============

# 默认权重配置
WEIGHT_CONFIG = {
    "turnover_rate": 20,
    "market_cap": 15,
    "limit_consecutive": 25,
    "price": 10,
    "volume_ratio": 15,
    "amplitude": 10,
    "sector": 5,
}


# ============ 得分计算逻辑 ============

def calculate_score(stock: Stock, strategy: Strategy) -> tuple[int, List[MatchDetail], int]:
    """计算股票与策略的匹配得分"""
    score = 0
    details = []
    max_score = 0

    # 1. 换手率 (权重20)
    max_score += WEIGHT_CONFIG["turnover_rate"]
    if strategy.min_turnover_rate and strategy.max_turnover_rate:
        if stock.turnover_rate:
            if strategy.min_turnover_rate <= stock.turnover_rate <= strategy.max_turnover_rate:
                score += WEIGHT_CONFIG["turnover_rate"]
                details.append(MatchDetail(
                    field="turnover_rate",
                    matched=True,
                    detail=f"换手率{stock.turnover_rate}%在区间内",
                    score=WEIGHT_CONFIG["turnover_rate"]
                ))
            elif stock.turnover_rate < strategy.min_turnover_rate:
                score += WEIGHT_CONFIG["turnover_rate"] // 2
                details.append(MatchDetail(
                    field="turnover_rate",
                    matched=False,
                    detail=f"换手率{stock.turnover_rate}%低于最小值{strategy.min_turnover_rate}%",
                    score=WEIGHT_CONFIG["turnover_rate"] // 2
                ))
            else:
                score += WEIGHT_CONFIG["turnover_rate"] // 2
                details.append(MatchDetail(
                    field="turnover_rate",
                    matched=False,
                    detail=f"换手率{stock.turnover_rate}%超过最大值{strategy.max_turnover_rate}%",
                    score=WEIGHT_CONFIG["turnover_rate"] // 2
                ))
        else:
            details.append(MatchDetail(
                field="turnover_rate",
                matched=False,
                detail="无换手率数据",
                score=0
            ))
    else:
        details.append(MatchDetail(
            field="turnover_rate",
            matched=False,
            detail="策略未设置换手率条件",
            score=0
        ))

    # 2. 流通市值 (权重15)
    max_score += WEIGHT_CONFIG["market_cap"]
    if strategy.min_market_cap and strategy.max_market_cap:
        if stock.market_cap:
            if strategy.min_market_cap <= stock.market_cap <= strategy.max_market_cap:
                score += WEIGHT_CONFIG["market_cap"]
                details.append(MatchDetail(
                    field="market_cap",
                    matched=True,
                    detail=f"市值{stock.market_cap}亿在区间内",
                    score=WEIGHT_CONFIG["market_cap"]
                ))
            elif stock.market_cap < strategy.min_market_cap:
                score += WEIGHT_CONFIG["market_cap"] // 2
                details.append(MatchDetail(
                    field="market_cap",
                    matched=False,
                    detail=f"市值{stock.market_cap}亿低于最小值{strategy.min_market_cap}亿",
                    score=WEIGHT_CONFIG["market_cap"] // 2
                ))
            else:
                score += WEIGHT_CONFIG["market_cap"] // 2
                details.append(MatchDetail(
                    field="market_cap",
                    matched=False,
                    detail=f"市值{stock.market_cap}亿超过最大值{strategy.max_market_cap}亿",
                    score=WEIGHT_CONFIG["market_cap"] // 2
                ))
        else:
            details.append(MatchDetail(
                field="market_cap",
                matched=False,
                detail="无市值数据",
                score=0
            ))
    else:
        details.append(MatchDetail(
            field="market_cap",
            matched=False,
            detail="策略未设置市值条件",
            score=0
        ))

    # 3. 涨停天数 (权重25) - 越高越好
    max_score += WEIGHT_CONFIG["limit_consecutive"]
    if strategy.limit_up_days is not None:
        if stock.limit_consecutive:
            if stock.limit_consecutive >= strategy.limit_up_days:
                # 超过要求，得满分；接近要求，部分得分
                bonus = min(10, (stock.limit_consecutive - strategy.limit_up_days) * 3)
                score += WEIGHT_CONFIG["limit_consecutive"] + bonus
                details.append(MatchDetail(
                    field="limit_consecutive",
                    matched=True,
                    detail=f"{stock.limit_consecutive}连板，超过要求的{strategy.limit_up_days}天",
                    score=WEIGHT_CONFIG["limit_consecutive"] + bonus
                ))
            else:
                score += (stock.limit_consecutive / strategy.limit_up_days) * WEIGHT_CONFIG["limit_consecutive"]
                details.append(MatchDetail(
                    field="limit_consecutive",
                    matched=False,
                    detail=f"{stock.limit_consecutive}连板，未达到要求的{strategy.limit_up_days}天",
                    score=int((stock.limit_consecutive / strategy.limit_up_days) * WEIGHT_CONFIG["limit_consecutive"])
                ))
        else:
            details.append(MatchDetail(
                field="limit_consecutive",
                matched=False,
                detail="无连板数据",
                score=0
            ))
    else:
        # 没有设置涨停天数要求，给部分分数
        score += WEIGHT_CONFIG["limit_consecutive"] // 2
        details.append(MatchDetail(
            field="limit_consecutive",
            matched=False,
            detail="策略未设置涨停天数要求",
            score=WEIGHT_CONFIG["limit_consecutive"] // 2
        ))

    # 4. 股价 (权重10)
    max_score += WEIGHT_CONFIG["price"]
    if strategy.min_price and strategy.max_price:
        if stock.price:
            if strategy.min_price <= stock.price <= strategy.max_price:
                score += WEIGHT_CONFIG["price"]
                details.append(MatchDetail(
                    field="price",
                    matched=True,
                    detail=f"股价{stock.price}元在区间内",
                    score=WEIGHT_CONFIG["price"]
                ))
            else:
                details.append(MatchDetail(
                    field="price",
                    matched=False,
                    detail=f"股价{stock.price}元不在区间内",
                    score=0
                ))
        else:
            details.append(MatchDetail(
                field="price",
                matched=False,
                detail="无股价数据",
                score=0
            ))
    else:
        score += WEIGHT_CONFIG["price"] // 2
        details.append(MatchDetail(
            field="price",
            matched=False,
            detail="策略未设置股价条件",
            score=WEIGHT_CONFIG["price"] // 2
        ))

    # 5. 量比 (权重15) - 越高越好
    max_score += WEIGHT_CONFIG["volume_ratio"]
    if strategy.min_volume_ratio:
        if stock.volume_ratio:
            if stock.volume_ratio >= strategy.min_volume_ratio:
                # 量比1-2得基础分，2以上加分
                ratio_score = min(WEIGHT_CONFIG["volume_ratio"],
                                int(stock.volume_ratio * WEIGHT_CONFIG["volume_ratio"] * 0.6))
                score += ratio_score
                details.append(MatchDetail(
                    field="volume_ratio",
                    matched=True,
                    detail=f"量比{stock.volume_ratio}符合要求",
                    score=ratio_score
                ))
            else:
                details.append(MatchDetail(
                    field="volume_ratio",
                    matched=False,
                    detail=f"量比{stock.volume_ratio}低于要求的{strategy.min_volume_ratio}",
                    score=0
                ))
        else:
            details.append(MatchDetail(
                field="volume_ratio",
                matched=False,
                detail="无量比数据",
                score=0
            ))
    else:
        score += WEIGHT_CONFIG["volume_ratio"] // 2
        details.append(MatchDetail(
            field="volume_ratio",
            matched=False,
            detail="策略未设置量比条件",
            score=WEIGHT_CONFIG["volume_ratio"] // 2
        ))

    # 6. 振幅 (权重10)
    max_score += WEIGHT_CONFIG["amplitude"]
    if strategy.min_amplitude and strategy.max_amplitude:
        if stock.amplitude:
            if strategy.min_amplitude <= stock.amplitude <= strategy.max_amplitude:
                score += WEIGHT_CONFIG["amplitude"]
                details.append(MatchDetail(
                    field="amplitude",
                    matched=True,
                    detail=f"振幅{stock.amplitude}%在区间内",
                    score=WEIGHT_CONFIG["amplitude"]
                ))
            else:
                details.append(MatchDetail(
                    field="amplitude",
                    matched=False,
                    detail=f"振幅{stock.amplitude}%不在区间内",
                    score=0
                ))
        else:
            details.append(MatchDetail(
                field="amplitude",
                matched=False,
                detail="无振幅数据",
                score=0
            ))
    else:
        score += WEIGHT_CONFIG["amplitude"] // 2
        details.append(MatchDetail(
            field="amplitude",
            matched=False,
            detail="策略未设置振幅条件",
            score=WEIGHT_CONFIG["amplitude"] // 2
        ))

    # 7. 板块匹配 (权重5)
    max_score += WEIGHT_CONFIG["sector"]
    if strategy.watch_signals and stock.sector:
        # watch_signals包含板块关键词
        signals = strategy.watch_signals.lower()
        sector = stock.sector.lower()
        if sector in signals or any(s in sector for s in signals.split(',')):
            score += WEIGHT_CONFIG["sector"]
            details.append(MatchDetail(
                field="sector",
                matched=True,
                detail=f"属于{stock.sector}板块，符合策略关注",
                score=WEIGHT_CONFIG["sector"]
            ))
        else:
            details.append(MatchDetail(
                field="sector",
                matched=False,
                detail=f"属于{stock.sector}板块，不在策略关注范围内",
                score=0
            ))
    else:
        details.append(MatchDetail(
            field="sector",
            matched=False,
            detail="无板块数据或策略未设置板块条件",
            score=0
        ))

    # 限制最大分数不超过100
    score = min(100, score)

    return score, details, max_score


def get_entry_advice(stock: Stock, strategy: Strategy) -> EntryAdvice:
    """根据策略和股票获取买入建议"""

    # 默认建议
    can_enter = False
    signal = "不符合买入条件"
    risk = None
    trigger_type = None

    # 检查涨幅
    change = stock.change or 0

    # 根据watch_signals判断买入场景
    watch_signals = (strategy.watch_signals or "").lower()

    # 龙头战法 - 打板
    if "龙头" in watch_signals or "连板" in watch_signals:
        trigger_type = "打板"
        if change >= 9.5:
            can_enter = True
            signal = "今日涨停，可打板介入"
            risk = "注意炸板风险"
        elif change >= 5:
            can_enter = True
            signal = "涨幅较大，需充分换手后可考虑"
            risk = "打板风险较高"
        elif change >= 0:
            can_enter = False
            signal = "涨幅不够，等待涨停信号"
            risk = "可能不会涨停"

    # 低吸
    elif "低吸" in watch_signals or "回调" in watch_signals:
        trigger_type = "低吸"
        if change < 0:
            can_enter = True
            signal = "回调企稳，可考虑低吸"
            risk = "需等待止跌信号"
        elif change < 3:
            can_enter = True
            signal = "涨幅较小，可考虑低吸"
            risk = "可能继续下跌"
        else:
            can_enter = False
            signal = "涨幅已高，不适合低吸"

    # 突破
    elif "突破" in watch_signals:
        trigger_type = "突破"
        if change >= 5 and change < 9:
            can_enter = True
            signal = "放量突破，可半路介入"
            risk = "需观察承接力度"
        elif change >= 9:
            can_enter = True
            signal = "涨停突破，可打板确认"
            risk = "可能炸板"

    # 默认情况 - 根据涨幅判断
    else:
        if change >= 9.5:
            can_enter = True
            trigger_type = "打板"
            signal = "涨停板，可打板介入"
            risk = "注意炸板风险"
        elif change >= 5:
            can_enter = True
            trigger_type = "半路"
            signal = "强势上涨，可半路介入"
            risk = "成本较高"
        elif change >= 0:
            can_enter = True
            trigger_type = "低吸"
            signal = "可考虑低吸"
            risk = "可能继续调整"
        else:
            can_enter = True
            trigger_type = "低吸"
            signal = "回调中，可考虑低吸"
            risk = "需等待止跌"

    return EntryAdvice(
        can_enter=can_enter,
        signal=signal,
        risk=risk,
        trigger_type=trigger_type
    )


def get_exit_advice(strategy: Strategy) -> ExitAdvice:
    """获取卖出建议"""
    return ExitAdvice(
        stop_loss=f"{strategy.stop_loss}%" if strategy.stop_loss else "6%",
        take_profit_1=f"{strategy.take_profit_1}%" if strategy.take_profit_1 else "7%",
        take_profit_2=f"{strategy.take_profit_2}%" if strategy.take_profit_2 else "15%",
        trailing_stop=f"{strategy.trailing_stop}%" if strategy.trailing_stop else "5%",
        advice=f"止损{strategy.stop_loss or 6}%，{strategy.take_profit_1 or 7}%可考虑部分止盈"
    )


# ============ API 接口 ============

class ScanRequest(BaseModel):
    strategy_id: int
    stock_ids: Optional[List[int]] = None  # 指定股票ID，不指定则扫描全部


@router.post("/scan", response_model=ScanResponse)
def scan_strategy(req: ScanRequest, db: Session = Depends(get_db)):
    """扫描策略匹配的股票"""

    # 获取策略
    strategy = db.get(Strategy, req.strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    # 获取股票列表
    if req.stock_ids:
        stocks = db.exec(
            select(Stock).where(Stock.id.in_(req.stock_ids))
        ).all()
    else:
        stocks = db.exec(select(Stock)).all()

    if not stocks:
        raise HTTPException(status_code=404, detail="No stocks found")

    # 计算每只股票的得分
    results = []
    for stock in stocks:
        score, details, max_score = calculate_score(stock, strategy)
        entry_advice = get_entry_advice(stock, strategy)
        exit_advice = get_exit_advice(strategy)

        results.append(ScanResult(
            stock_id=stock.id,
            code=stock.code,
            name=stock.name,
            sector=stock.sector,
            price=stock.price,
            change=stock.change,
            turnover_rate=stock.turnover_rate,
            volume_ratio=stock.volume_ratio,
            market_cap=stock.market_cap,
            limit_consecutive=stock.limit_consecutive,
            score=score,
            max_score=max_score,
            match_details=details,
            entry_advice=entry_advice,
            exit_advice=exit_advice
        ))

    # 按得分排序
    results.sort(key=lambda x: x.score, reverse=True)

    return ScanResponse(
        strategy_id=strategy.id,
        strategy_name=strategy.name,
        results=results
    )
