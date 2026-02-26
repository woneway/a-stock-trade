from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from datetime import date, timedelta
import json

from app.database import engine
from app.models.plan import PrePlan, PostReview, HistoricalPlan
from app.models.strategy import Strategy
from app.models.trade import Trade
from app.schemas.plan import (
    PrePlanCreate,
    PrePlanUpdate,
    PrePlanResponse,
    PostReviewCreate,
    PostReviewUpdate,
    PostReviewResponse,
    PostReviewAnalysis,
    CandidateStock,
    IntelligentAnalysis,
    HistoricalPlanCreate,
    HistoricalPlanUpdate,
    HistoricalPlanResponse,
)


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/plan", tags=["plan"])


@router.get("/pre/today", response_model=Optional[PrePlanResponse])
def get_today_plan(db: Session = Depends(get_db)):
    today = date.today()
    statement = select(PrePlan).where(
        PrePlan.trade_date == today,
        PrePlan.status.in_(["confirmed", "executed"])
    )
    result = db.exec(statement).first()
    return result


@router.get("/pre", response_model=Optional[PrePlanResponse])
def get_pre_plan(db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    statement = select(PrePlan).where(PrePlan.trade_date == trade_date)
    result = db.exec(statement).first()
    return result


@router.get("/pre/list", response_model=List[PrePlanResponse])
def get_pre_plans(db: Session = Depends(get_db), start_date: date = None, end_date: date = None):
    statement = select(PrePlan)
    if start_date:
        statement = statement.where(PrePlan.plan_date >= start_date)
    if end_date:
        statement = statement.where(PrePlan.plan_date <= end_date)
    statement = statement.order_by(PrePlan.plan_date.desc())
    results = db.exec(statement).all()
    return results


@router.post("/pre", response_model=PrePlanResponse)
def create_pre_plan(item: PrePlanCreate, db: Session = Depends(get_db)):
    existing = db.exec(
        select(PrePlan).where(
            PrePlan.plan_date == item.plan_date,
            PrePlan.trade_date == item.trade_date
        )
    ).first()

    if existing:
        for key, value in item.model_dump().items():
            if value is not None:
                setattr(existing, key, value)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    db_item = PrePlan.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/pre/{plan_id}", response_model=PrePlanResponse)
def update_pre_plan(plan_id: int, item: PrePlanUpdate, db: Session = Depends(get_db)):
    db_item = db.get(PrePlan, plan_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Plan not found")

    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.post("/pre/{plan_id}/confirm", response_model=PrePlanResponse)
def confirm_plan(plan_id: int, db: Session = Depends(get_db)):
    db_item = db.get(PrePlan, plan_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Plan not found")

    db_item.status = "confirmed"
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/pre/{plan_id}")
def delete_pre_plan(plan_id: int, db: Session = Depends(get_db)):
    db_item = db.get(PrePlan, plan_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Plan not found")

    db.delete(db_item)
    db.commit()
    return {"message": "Plan deleted"}


@router.post("/generate-from-strategies", response_model=PrePlanResponse)
def generate_plan_from_strategies(
    strategy_ids: str,
    trade_date: date = None,
    db: Session = Depends(get_db)
):
    if trade_date is None:
        trade_date = date.today() + timedelta(days=1)

    plan_date = date.today()

    strategy_id_list = [int(s.strip()) for s in strategy_ids.split(",") if s.strip()]
    strategies = db.exec(
        select(Strategy).where(Strategy.id.in_(strategy_id_list))
    ).all()

    if not strategies:
        raise HTTPException(status_code=404, detail="No strategies found")

    strategy_names = ",".join([s.name for s in strategies])
    combined_logic = " | ".join([
        s.stock_selection_logic for s in strategies if s.stock_selection_logic
    ])

    avg_stop_loss = sum(s.stop_loss for s in strategies) / len(strategies)
    avg_position = sum(s.position_size for s in strategies) / len(strategies)

    candidate_stocks = []
    for s in strategies:
        if s.stock_selection_logic:
            candidate_stocks.append(CandidateStock(
                code="",
                name=f"[{s.name}候选]",
                buy_reason=s.entry_condition or s.stock_selection_logic,
                sell_reason=s.exit_condition or "",
                priority=1 if s.is_active else 0
            ))

    existing = db.exec(
        select(PrePlan).where(
            PrePlan.plan_date == plan_date,
            PrePlan.trade_date == trade_date
        )
    ).first()

    if existing:
        existing.strategy_ids = strategy_ids
        existing.selected_strategy = strategy_names
        existing.candidate_stocks = json.dumps([c.model_dump() for c in candidate_stocks])
        existing.stop_loss = avg_stop_loss
        existing.position_size = avg_position
        existing.entry_condition = combined_logic
        existing.status = "draft"
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    new_plan = PrePlan(
        strategy_ids=strategy_ids,
        selected_strategy=strategy_names,
        sentiment="分歧",
        candidate_stocks=json.dumps([c.model_dump() for c in candidate_stocks]),
        stop_loss=avg_stop_loss,
        position_size=avg_position,
        entry_condition=combined_logic,
        status="draft",
        plan_date=plan_date,
        trade_date=trade_date,
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan


@router.get("/post", response_model=PostReviewResponse)
def get_post_review(db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    statement = select(PostReview).where(PostReview.trade_date == trade_date)
    result = db.exec(statement).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return result


@router.post("/post", response_model=PostReviewResponse)
def create_post_review(item: PostReviewCreate, db: Session = Depends(get_db)):
    existing = db.exec(
        select(PostReview).where(PostReview.trade_date == item.trade_date)
    ).first()

    if existing:
        for key, value in item.model_dump().items():
            if value is not None:
                setattr(existing, key, value)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    db_item = PostReview.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/post", response_model=PostReviewResponse)
def update_post_review(item: PostReviewUpdate, db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()

    db_item = db.exec(
        select(PostReview).where(PostReview.trade_date == trade_date)
    ).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Post review not found")

    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def _calc_post_review_analysis(db: Session, trade_date: date) -> PostReviewAnalysis:
    pre_plan = db.exec(
        select(PrePlan).where(PrePlan.trade_date == trade_date)
    ).first()

    trades = db.exec(
        select(Trade).where(Trade.trade_date == trade_date)
    ).all()

    planned_stocks = []
    if pre_plan and pre_plan.candidate_stocks:
        try:
            stocks_data = json.loads(pre_plan.candidate_stocks)
            planned_stocks = [s["code"] for s in stocks_data if s.get("code")]
        except:
            pass

    actual_traded = []
    planned_executed = []
    unplanned_executed = []
    planned_pnl = 0.0
    unplanned_pnl = 0.0

    for trade in trades:
        stock_code = trade.code
        if stock_code not in actual_traded:
            actual_traded.append(stock_code)

        if stock_code in planned_stocks:
            if trade.action == "buy":
                planned_executed.append(stock_code)
            if trade.pnl:
                planned_pnl += trade.pnl
        else:
            if trade.action == "buy":
                unplanned_executed.append(stock_code)
            if trade.pnl:
                unplanned_pnl += trade.pnl

    total_planned = len(planned_stocks) if planned_stocks else 0
    total_executed = len(planned_executed)
    execution_rate = (total_executed / total_planned * 100) if total_planned > 0 else 0.0

    return PostReviewAnalysis(
        planned_stocks=planned_stocks,
        actual_traded_stocks=actual_traded,
        planned_executed=planned_executed,
        unplanned_executed=unplanned_executed,
        execution_rate=round(execution_rate, 1),
        planned_pnl=round(planned_pnl, 2),
        unplanned_pnl=round(unplanned_pnl, 2),
        total_pnl=round(planned_pnl + unplanned_pnl, 2),
    )


@router.get("/post/analysis", response_model=PostReviewAnalysis)
def get_post_review_analysis(db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    return _calc_post_review_analysis(db, trade_date)


@router.get("/intelligent-analysis", response_model=IntelligentAnalysis)
def get_intelligent_analysis(db: Session = Depends(get_db), days: int = 30):
    today = date.today()
    start_date = today - timedelta(days=days)

    today_analysis = _calc_post_review_analysis(db, today)

    all_trades = db.exec(
        select(Trade).where(Trade.trade_date >= start_date)
    ).all()

    week_start = today - timedelta(days=7)
    month_start = today - timedelta(days=30)

    week_trades = [t for t in all_trades if t.trade_date >= week_start]
    month_trades = all_trades

    def calc_stats(trades_list):
        if not trades_list:
            return {"trade_count": 0, "win_count": 0, "loss_count": 0, "win_rate": 0.0, "total_pnl": 0.0, "avg_pnl": 0.0}
        win_count = sum(1 for t in trades_list if t.pnl and t.pnl > 0)
        loss_count = sum(1 for t in trades_list if t.pnl and t.pnl < 0)
        total_pnl = sum(t.pnl if t.pnl else 0 for t in trades_list)
        return {
            "trade_count": len(trades_list),
            "win_count": win_count,
            "loss_count": loss_count,
            "win_rate": round(win_count / len(trades_list) * 100, 1) if trades_list else 0.0,
            "total_pnl": round(total_pnl, 2),
            "avg_pnl": round(total_pnl / len(trades_list), 2) if trades_list else 0.0,
        }

    weekly_stats = calc_stats(week_trades)
    monthly_stats = calc_stats(month_trades)

    strategies = db.exec(select(Strategy)).all()
    strategy_map = {s.id: s.name for s in strategies}

    pre_plans = db.exec(
        select(PrePlan).where(PrePlan.trade_date >= start_date)
    ).all()
    plan_strategy_map = {p.trade_date: p.selected_strategy for p in pre_plans if p.selected_strategy}

    strategy_trades = {}
    for trade in all_trades:
        strategy_name = plan_strategy_map.get(trade.trade_date, "未指定")
        if strategy_name not in strategy_trades:
            strategy_trades[strategy_name] = []
        strategy_trades[strategy_name].append(trade)

    strategy_stats = []
    for strategy_name, trades_list in strategy_trades.items():
        if not trades_list:
            continue
        wins = [t for t in trades_list if t.pnl and t.pnl > 0]
        losses = [t for t in trades_list if t.pnl and t.pnl < 0]
        total = sum(t.pnl if t.pnl else 0 for t in trades_list)
        strategy_stats.append(StrategyStats(
            strategy_name=strategy_name,
            trade_count=len(trades_list),
            win_count=len(wins),
            loss_count=len(losses),
            win_rate=round(len(wins) / len(trades_list) * 100, 1) if trades_list else 0.0,
            total_pnl=round(total, 2),
            avg_pnl=round(total / len(trades_list), 2) if trades_list else 0.0,
            avg_win=round(sum(t.pnl for t in wins) / len(wins), 2) if wins else 0.0,
            avg_loss=round(sum(t.pnl for t in losses) / len(losses), 2) if losses else 0.0,
        ))

    strategy_stats.sort(key=lambda x: x.total_pnl, reverse=True)

    recommendations = []
    if monthly_stats["win_rate"] < 40:
        recommendations.append("本月胜率偏低，建议收紧止损线，减少单笔仓位")
    if monthly_stats["win_rate"] > 60:
        recommendations.append("本月胜率较高，保持当前策略，可适度放大仓位")
    if weekly_stats["trade_count"] > 10:
        recommendations.append("本周交易频繁，建议减少非必要交易，专注核心机会")
    if weekly_stats["trade_count"] < 2:
        recommendations.append("本周交易较少，可能是机会较少，建议耐心等待")

    if strategy_stats:
        best_strategy = strategy_stats[0]
        worst_strategy = strategy_stats[-1]
        if best_strategy.total_pnl > 0:
            recommendations.append(f"策略'{best_strategy.strategy_name}'表现最佳，可重点使用")
        if worst_strategy.total_pnl < 0 and worst_strategy.trade_count >= 3:
            recommendations.append(f"策略'{worst_strategy.strategy_name}'表现较差，建议减少使用或优化参数")

    if today_analysis.execution_rate < 50 and today_analysis.planned_stocks:
        recommendations.append("计划执行率偏低，建议严格按照计划执行，减少临时起意")

    if not recommendations:
        recommendations.append("继续保持当前操作节奏，关注市场情绪变化")

    return IntelligentAnalysis(
        today_analysis=today_analysis,
        weekly_stats=weekly_stats,
        monthly_stats=monthly_stats,
        strategy_stats=strategy_stats,
        recommendations=recommendations,
    )


# ========== 历史计划 API ==========

@router.get("/history", response_model=List[HistoricalPlanResponse])
def get_historical_plans(
    db: Session = Depends(get_db),
    start_date: date = None,
    end_date: date = None,
    limit: int = 30
):
    """获取历史计划列表"""
    statement = select(HistoricalPlan)
    if start_date:
        statement = statement.where(HistoricalPlan.trade_date >= start_date)
    if end_date:
        statement = statement.where(HistoricalPlan.trade_date <= end_date)
    statement = statement.order_by(HistoricalPlan.trade_date.desc()).limit(limit)
    results = db.exec(statement).all()
    return results


@router.get("/history/{history_id}", response_model=HistoricalPlanResponse)
def get_historical_plan(history_id: int, db: Session = Depends(get_db)):
    """获取历史计划详情"""
    db_item = db.get(HistoricalPlan, history_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Historical plan not found")
    return db_item


@router.post("/history", response_model=HistoricalPlanResponse)
def create_historical_plan(item: HistoricalPlanCreate, db: Session = Depends(get_db)):
    """创建历史计划"""
    existing = db.exec(
        select(HistoricalPlan).where(HistoricalPlan.trade_date == item.trade_date)
    ).first()

    if existing:
        for key, value in item.model_dump().items():
            if value is not None:
                setattr(existing, key, value)
        existing.updated_at = date.today()
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    db_item = HistoricalPlan.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/history/{history_id}/sync", response_model=HistoricalPlanResponse)
def sync_historical_plan(history_id: int, db: Session = Depends(get_db)):
    """同步历史计划数据（从PrePlan/Trades计算汇总）"""
    db_item = db.get(HistoricalPlan, history_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Historical plan not found")

    # 从PrePlan获取计划数据
    if db_item.pre_plan_id:
        pre_plan = db.get(PrePlan, db_item.pre_plan_id)
        if pre_plan and pre_plan.candidate_stocks:
            try:
                stocks_data = json.loads(pre_plan.candidate_stocks)
                db_item.planned_stock_count = len([s for s in stocks_data if s.get("code")])
            except:
                db_item.planned_stock_count = 0

    # 从Trade获取执行数据
    trades = db.exec(
        select(Trade).where(Trade.trade_date == db_item.trade_date)
    ).all()
    db_item.executed_stock_count = len(set(t.code for t in trades if t.action == "buy"))

    # 计算执行率
    if db_item.planned_stock_count and db_item.planned_stock_count > 0:
        db_item.execution_rate = round(
            db_item.executed_stock_count / db_item.planned_stock_count * 100, 1
        )

    # 计算总盈亏
    total_pnl = sum(t.pnl if t.pnl else 0 for t in trades)
    db_item.total_pnl = round(total_pnl, 2)

    db_item.updated_at = date.today()
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/history/{history_id}", response_model=HistoricalPlanResponse)
def update_historical_plan(history_id: int, item: HistoricalPlanUpdate, db: Session = Depends(get_db)):
    """更新历史计划"""
    db_item = db.get(HistoricalPlan, history_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Historical plan not found")

    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)

    db_item.updated_at = date.today()
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
