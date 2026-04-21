"""Databasmotor och sessionshantering."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_db_and_tables() -> None:
    """Skapa alla tabeller vid uppstart."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield en databassession."""
    async with async_session_factory() as session:
        yield session
