"""Databasmotor och sessionshantering. Schemat ägs av Alembic, se migrations/."""

from collections.abc import Generator

from sqlmodel import Session, create_engine

from config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.SQL_ECHO)


def get_session() -> Generator[Session]:
    """En session per request. Servicen committar, inte repositoryt."""
    with Session(engine) as session:
        yield session
