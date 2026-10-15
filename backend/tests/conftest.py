"""Testriggen: riktig Postgres, egen testdatabas, varje test rullas tillbaka.

Sviten kör mot appens databasnamn + `_test` och vägrar annat namn, så att en
felriktad körning aldrig rör utvecklings- eller driftdata. Schemat byggs med
Alembic, samma väg som i drift.
"""

from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.engine import make_url
from sqlmodel import Session, create_engine

from api import app
from config import settings
from database import get_session

BACKEND = Path(__file__).resolve().parents[1]
APP_URL = make_url(settings.DATABASE_URL)
TEST_URL = APP_URL.set(database=f"{APP_URL.database}_test")


def _create_test_database() -> None:
    admin = create_engine(APP_URL.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": TEST_URL.database},
        )
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{TEST_URL.database}"'))
    admin.dispose()


@pytest.fixture(scope="session")
def engine() -> Generator[Engine]:
    assert TEST_URL.database and TEST_URL.database.endswith("_test"), TEST_URL.database
    try:
        _create_test_database()
    except Exception as error:
        raise RuntimeError("Ingen databas. Starta den med: docker compose up -d db") from error

    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "migrations"))
    config.set_main_option("sqlalchemy.url", TEST_URL.render_as_string(hide_password=False))
    command.upgrade(config, "head")

    engine = create_engine(TEST_URL)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Generator[Session]:
    """En session vars ändringar rullas tillbaka efter testet, även efter commit()."""
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
            yield session
        transaction.rollback()


@pytest.fixture
def client(session: Session) -> Generator[TestClient]:
    """API-klient som använder testets session."""
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
