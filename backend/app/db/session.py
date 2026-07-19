"""Async DB session for the backend API.

Deliberately independent of storage/scripts/db_connect.py: that module is
shared sync infrastructure used well beyond the backend (ingestion
connectors, migrations, models_layer training scripts, one-off scripts),
and converting it to async would ripple far outside this backend-hardening
pass's scope. The backend gets its own asyncpg-backed engine here instead,
pointed at the same DATABASE_URL.
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.core.config import settings


def _to_async_url(database_url: str) -> str:
    """postgresql://... and postgresql+psycopg2://... both need to become
    postgresql+asyncpg://... for the async engine - asyncpg is a different
    wire-protocol driver from the sync psycopg2 driver used everywhere else
    in the repo, so the DSN scheme has to say so explicitly."""
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url
    if database_url.startswith("postgresql+psycopg2://"):
        return database_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return database_url


_engine = None
_AsyncSessionLocal = None


def get_async_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            _to_async_url(settings.DATABASE_URL),
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
        )
    return _engine


def get_async_session_factory():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(bind=get_async_engine(), expire_on_commit=False)
    return _AsyncSessionLocal


async def get_db():
    async with get_async_session_factory()() as db:
        yield db
