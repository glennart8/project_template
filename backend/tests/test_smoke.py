"""Smoke-test som verifierar att grundläggande infrastruktur fungerar."""

from fastapi.testclient import TestClient
from sqlmodel import Session

from api import app


def test_session_fixture_ger_session(session: Session) -> None:
    assert isinstance(session, Session)


def test_health_svarar_under_api() -> None:
    with TestClient(app) as client:
        assert client.get("/api/health").json() == {"status": "ok"}


def test_version_svarar_under_api() -> None:
    with TestClient(app) as client:
        assert client.get("/api/version").status_code == 200
