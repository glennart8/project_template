"""Databasmotor och sessionshantering. Schemat ägs av Alembic, se migrations/."""

from collections.abc import Generator

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, create_engine

from config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


def get_session() -> Generator[Session]:
    """En session per request. Servicen committar, inte repositoryt."""
    with Session(engine) as session:
        yield session


def is_database_up(session: Session) -> bool:
    """För hälsokontrollen: svarar databasen?"""
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return False
    return True
