"""Mallens gemensamma byggstenar: inställningar, inloggning, felhantering, klocka."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

import clock
from config import Settings, settings
from errors import register_exception_handlers


def test_mock_inloggning_stoppas_i_produktion() -> None:
    with pytest.raises(ValidationError, match="AUTH_MODE"):
        Settings(ENVIRONMENT="production", AUTH_MODE="mock")


def test_app_proxy_tillats_i_produktion() -> None:
    assert Settings(ENVIRONMENT="production", AUTH_MODE="app_proxy")


def test_app_proxy_utan_header_ger_401(client: TestClient) -> None:
    assert client.get("/api/me").status_code == 401


def test_app_proxy_oversatter_grupper_till_roller(client: TestClient) -> None:
    response = client.get(
        "/api/me",
        headers={
            "x-control-header": "HEPI02",
            "x-control-displayname-header": "Henrik",
            "x-control-group-header": "annan-grupp, admin-grupp",
        },
    )
    assert response.json() == {"username": "HEPI02", "name": "Henrik", "roles": ["admin"]}


def test_okand_grupp_ger_ingen_roll(client: TestClient) -> None:
    headers = {"x-control-header": "HEPI02", "x-control-group-header": "annan-grupp"}
    assert client.get("/api/me", headers=headers).json()["roles"] == []


def test_mock_ger_fast_anvandare(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(settings, "AUTH_MODE", "mock")
    monkeypatch.setattr(settings, "MOCK_USER", "TEST01")
    assert client.get("/api/me").json()["username"] == "TEST01"


@pytest.mark.parametrize(
    ("error", "status"),
    [(LookupError, 404), (PermissionError, 403), (ValueError, 422)],
)
def test_servicefel_oversatts_till_http(error: type[Exception], status: int) -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/fel")
    def fel() -> None:
        raise error("Begripligt meddelande")

    response = TestClient(app).get("/fel")
    assert response.status_code == status
    assert response.json() == {"detail": "Begripligt meddelande"}


def test_klockan_har_tidszon() -> None:
    assert clock.now().tzinfo is not None
