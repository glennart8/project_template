"""Smoke-test som verifierar att grundläggande infrastruktur fungerar."""

from fastapi.testclient import TestClient
from sqlalchemy import func
from sqlmodel import Session, select


def test_sviten_kor_mot_testdatabasen(session: Session) -> None:
    assert session.exec(select(func.current_database())).one().endswith("_test")


def test_health_svarar_under_api(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}


def test_version_svarar_under_api(client: TestClient) -> None:
    assert client.get("/api/version").status_code == 200
