"""
游资复盘 API 路由
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.agents.models import AnalyzeRequest, AnalyzeResponse, ReviewResult
from app.agents.review_agent import get_review_agent

router = APIRouter(prefix="/api/review", tags=["游资复盘"])


def _get_today() -> str:
    """获取今天的日期"""
    return datetime.now().strftime("%Y%m%d")


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_market(
    date: Optional[str] = None,
    max_iterations: int = 15
):
    """
    游资复盘分析接口

    - **date**: 复盘日期，格式 YYYYMMDD，默认今天
    - **max_iterations**: 最大迭代次数，默认 15
    """
    # 参数验证
    if date is None:
        date = _get_today()

    # 验证日期格式
    if len(date) != 8 or not date.isdigit():
        raise HTTPException(status_code=422, detail="日期格式错误，应为 YYYYMMDD")

    try:
        # 获取 Agent
        agent = get_review_agent()

        # 执行分析
        result = await agent.run(date)

        # 返回结果
        return AnalyzeResponse(
            code=0,
            msg="success",
            data=result
        )

    except Exception as e:
        return AnalyzeResponse(
            code=1,
            msg="error",
            error=str(e)
        )


@router.get("/history")
async def get_review_history(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 30
):
    """
    获取历史复盘记录

    - **start_date**: 开始日期
    - **end_date**: 结束日期
    - **limit**: 返回数量限制
    """
    # TODO: 实现历史记录查询
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "list": [],
            "total": 0
        }
    }


@router.post("/compare")
async def compare_with_history(
    date: str
):
    """
    与历史相似日期对比分析

    - **date**: 要对比的日期
    """
    # TODO: 实现历史对比
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "message": "功能开发中"
        }
    }
