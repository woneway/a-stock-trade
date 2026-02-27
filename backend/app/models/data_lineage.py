"""数据血缘追踪模型"""
from datetime import datetime
from sqlmodel import Field, SQLModel


class DataLineage(SQLModel, table=True):
    """数据血缘表 - 追踪数据来源和更新时间"""
    __tablename__ = "data_lineage"

    id: int | None = Field(default=None, primary_key=True)
    func_name: str = Field(index=True, description="接口名称")
    params_hash: str = Field(description="参数哈希")
    source: str = Field(default="cache", description="数据来源: cache/akshare")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")
    record_count: int = Field(default=0, description="记录数")

    # 复合唯一索引
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
