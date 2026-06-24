from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

from .config import settings

naming_convention = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata_obj = MetaData(naming_convention=naming_convention)


class Base(DeclarativeBase):
    metadata = metadata_obj


_engine = None
_sessionmaker = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=getattr(settings, "LOG_SQL_QUERIES", False),
            echo_pool=getattr(settings, "LOG_SQL_QUERIES", False),
            connect_args={"ssl": "prefer"},
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20,
        )
    return _engine


def get_sessionmaker():
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            get_engine(),
            expire_on_commit=False
        )
    return _sessionmaker


async def get_session():
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise