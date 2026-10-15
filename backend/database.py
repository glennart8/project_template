"""Databasmotor och sessionshantering."""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


def create_db_and_tables() -> None:
    """Skapa alla tabeller vid uppstart."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session]:
    """En session per request. Servicen committar, inte repositoryt."""
    with Session(engine) as session:
        yield session
