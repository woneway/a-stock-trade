from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from app.config import settings
from app.models import daily, backtest_strategy, external_data, external_yz_common  # noqa: F401

connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    poolclass=StaticPool,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
