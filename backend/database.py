"""Databasmotor och sessionshantering."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from backend.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)


async def create_db_and_tables() -> None:
    """Skapa alla tabeller vid uppstart."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """Yield en databassession."""
    async with SQLModelAsyncSession(engine) as session:
        yield session  # type: ignore[misc]
