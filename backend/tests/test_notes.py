"""Exemplets tester — mönstret för ett områdes tester."""

import uuid

import pytest
from fastapi.testclient import TestClient

USER = {"x-control-header": "TEST01"}


def test_skapad_anteckning_loggas_med_id_men_utan_text(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    # Fångar två fel: att INFO inte syns alls, och att innehåll hamnar i loggen.
    note = client.post("/api/notes", json={"text": "Hemlig text"}, headers=USER).json()
    logged = " ".join(record.getMessage() for record in caplog.records)
    assert note["id"] in logged
    assert "Hemlig text" not in logged


def test_anteckning_skapas_och_kan_hamtas(client: TestClient) -> None:
    created = client.post("/api/notes", json={"text": "  Hej  "}, headers=USER)
    assert created.status_code == 201
    assert created.json()["text"] == "Hej"
    assert created.json()["created_by"] == "TEST01"

    fetched = client.get(f"/api/notes/{created.json()['id']}", headers=USER)
    assert fetched.json() == created.json()


def test_tom_anteckning_ger_422(client: TestClient) -> None:
    response = client.post("/api/notes", json={"text": "   "}, headers=USER)
    assert response.status_code == 422
    assert response.json() == {"detail": "Anteckningen får inte vara tom."}


def test_okand_anteckning_ger_404(client: TestClient) -> None:
    assert client.get(f"/api/notes/{uuid.uuid4()}", headers=USER).status_code == 404


def test_utan_inloggning_ger_401(client: TestClient) -> None:
    assert client.get("/api/notes").status_code == 401
