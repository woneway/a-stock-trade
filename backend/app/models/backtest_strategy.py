from datetime import date
from sqlmodel import Field, SQLModel
from typing import Optional


class BacktestStrategy(SQLModel, table=True):
    """回测策略模型 - 存储用户自定义的Python策略脚本"""
    __tablename__ = "backtest_strategies"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None

    # 策略代码 (Python脚本，符合backtesting.py的Strategy格式)
    code: str

    # 策略类型: custom=自定义, builtin=内置
    strategy_type: str = Field(default="custom", alias="strategyType")

    # 策略参数定义 (JSON格式，用于前端动态生成表单)
    # 格式: [{"name": "n1", "label": "短期周期", "default": 10, "min": 5, "max": 50, "type": "int"}]
    params_definition: Optional[str] = Field(default="[]", alias="paramsDefinition")

    # 是否为默认/预置策略
    is_builtin: bool = Field(default=False, alias="isBuiltin")

    is_active: bool = Field(default=True, alias="isActive")

    created_at: date = Field(default_factory=date.today, alias="createdAt")
    updated_at: date = Field(default_factory=date.today, alias="updatedAt")

    class Config:
        populate_by_name = True
