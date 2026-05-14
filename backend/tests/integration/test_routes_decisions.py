"""Rotas /api/decisions."""

from __future__ import annotations

import pytest

from tests.conftest import make_player


@pytest.mark.integration
def test_post_decisao_valida(client):
    make_player(client, "Duser")
    r = client.post(
        "/api/decisions",
        json={
            "nome": "Duser",
            "evento_id": "CS_D01_E1",
            "opcao_id": "opt_ok_CS_D01_E1_a",
        },
    )
    assert r.status_code == 200
    body = r.get_json()
    assert "save" in body
    assert body["proximo_evento"] is not None
    assert body["proximo_evento"]["id"] == "CS_D01_E2"
    assert body.get("final") is None


@pytest.mark.integration
def test_post_decisao_campos_faltando_400(client):
    r = client.post("/api/decisions", json={"nome": "x"})
    assert r.status_code == 400


@pytest.mark.integration
def test_post_decisao_evento_errado_400(client):
    make_player(client, "BadEv")
    r = client.post(
        "/api/decisions",
        json={
            "nome": "BadEv",
            "evento_id": "CS_D05_E3",
            "opcao_id": "opt_ok_CS_D05_E3_a",
        },
    )
    assert r.status_code == 400


@pytest.mark.integration
def test_get_historico_decisoes(client):
    make_player(client, "Hist")
    client.post(
        "/api/decisions",
        json={
            "nome": "Hist",
            "evento_id": "CS_D01_E1",
            "opcao_id": "opt_ok_CS_D01_E1_b",
        },
    )
    r = client.get("/api/decisions/Hist")
    assert r.status_code == 200
    decisoes = r.get_json()["decisoes"]
    assert len(decisoes) == 1
    assert decisoes[0]["evento_id"] == "CS_D01_E1"
