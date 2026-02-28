"""
Agent 数据模型定义
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class AgentState(str, Enum):
    """Agent 状态"""
    IDLE = "idle"
    FETCHING_DATA = "fetching_data"
    ANALYZING = "analyzing"
    FETCHING_NEWS = "fetching_news"
    FETCHING_MORE_DATA = "fetching_more_data"
    COMPLETED = "completed"
    ERROR = "error"


class Action(str, Enum):
    """决策动作"""
    COMPLETE = "complete"
    FETCH_NEWS = "fetch_news"
    FETCH_MORE_DATA = "fetch_more_data"
    RETRY = "retry"


class ReviewStep(BaseModel):
    """复盘步骤"""
    step: int
    state: AgentState
    action: str
    result: str
    data_used: List[str]
    next_action: Optional[str] = None


class ReviewContext(BaseModel):
    """复盘上下文"""
    date: str
    steps: List[ReviewStep] = []

    # 收集的数据
    market_emotion: Optional[Dict[str, Any]] = None
    zt_pool: Optional[List[Dict[str, Any]]] = None
    dtgc: Optional[List[Dict[str, Any]]] = None
    zbgc: Optional[List[Dict[str, Any]]] = None
    fund_flow: Optional[Dict[str, Any]] = None
    lhb: Optional[List[Dict[str, Any]]] = None
    margin: Optional[Dict[str, Any]] = None
    sectors: Optional[List[Dict[str, Any]]] = None
    news: Optional[List[Dict[str, Any]]] = None

    # 分析结果
    analysis: Optional[Dict[str, Any]] = None
    final_report: Optional[str] = None


class DecisionResult(BaseModel):
    """LLM 决策结果"""
    action: Action
    reason: str
    params: Dict[str, Any] = {}
    analysis_update: str = ""


class ReviewResult(BaseModel):
    """复盘结果"""
    date: str
    iterations_used: int
    steps: List[ReviewStep]
    analysis: Optional[Dict[str, Any]] = None
    final_report: Optional[str] = None
    error: Optional[str] = None


class AnalyzeRequest(BaseModel):
    """分析请求"""
    date: Optional[str] = None
    max_iterations: int = 15


class AnalyzeResponse(BaseModel):
    """分析响应"""
    code: int = 0
    msg: str = "success"
    data: Optional[ReviewResult] = None
    error: Optional[str] = None
