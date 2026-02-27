from typing import Generator
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from app.config import settings
from app.models import daily, backtest_strategy, trading, data_lineage  # noqa: F401

connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    poolclass=StaticPool,
)


def get_db() -> Generator[Session, None]:
    """统一的数据库会话依赖"""
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
