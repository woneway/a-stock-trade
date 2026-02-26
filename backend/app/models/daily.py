from datetime import date
from sqlmodel import Field, SQLModel
from typing import Optional


class Plan(SQLModel, table=True):
    """计划/复盘统一模型"""
    __tablename__ = "plans"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 类型：plan=计划, review=复盘
    type: str = Field(default="plan", index=True)

    # 交易日期
    trade_date: date = Field(index=True)

    # 状态
    status: str = Field(default="draft")  # draft, completed

    # 模板类型
    template: Optional[str] = Field(default=None)  # daily, weekly, monthly

    # 富文本内容
    content: Optional[str] = Field(default=None)

    # 关联的计划（复盘关联计划）
    related_id: Optional[int] = Field(default=None, foreign_key="plans.id")

    # 执行数据
    stock_count: Optional[int] = Field(default=0)
    execution_rate: Optional[float] = Field(default=0.0)
    pnl: Optional[float] = Field(default=0.0)

    # 标签
    tags: Optional[str] = Field(default=None)

    created_at: date = Field(default_factory=date.today)
    updated_at: date = Field(default_factory=date.today)

    class Config:
        populate_by_name = True
