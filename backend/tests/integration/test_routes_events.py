"""Rotas /api/events."""

from __future__ import annotations

import pytest

from tests.conftest import make_player


@pytest.mark.integration
def test_proximo_sem_nome_400(client):
    r = client.get("/api/events/proximo")
    assert r.status_code == 400


@pytest.mark.integration
def test_proximo_retorna_evento(client):
    make_player(client, "Evuser")
    r = client.get("/api/events/proximo?nome=Evuser")
    assert r.status_code == 200
    body = r.get_json()
    assert body["evento"] is not None
    assert body["evento"]["id"] == "CS_D01_E1"


@pytest.mark.integration
def test_get_evento_por_id(client):
    r = client.get("/api/events/CS_D01_E1")
    assert r.status_code == 200
    assert r.get_json()["id"] == "CS_D01_E1"


@pytest.mark.integration
def test_get_evento_inexistente_404(client):
    r = client.get("/api/events/EVENTO_FAKE")
    assert r.status_code == 404
