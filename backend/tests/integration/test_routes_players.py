"""Rotas /api/players."""

from __future__ import annotations

import pytest

from tests.conftest import make_player


@pytest.mark.integration
def test_post_cria_jogador_201(client):
    r = client.post("/api/players", json={"nome": "NovoJogadorX"})
    assert r.status_code == 201
    body = r.get_json()
    assert body["nome"] == "NovoJogadorX"
    assert "id" in body


@pytest.mark.integration
def test_post_idempotente_200(client):
    r1 = client.post("/api/players", json={"nome": "MesmoNome"})
    r2 = client.post("/api/players", json={"nome": "MesmoNome"})
    assert r1.status_code == 201
    assert r2.status_code == 200
    assert r1.get_json()["id"] == r2.get_json()["id"]


@pytest.mark.integration
def test_get_jogador_200_e_404(client):
    make_player(client, "Existe")
    ok = client.get("/api/players/Existe")
    assert ok.status_code == 200
    missing = client.get("/api/players/NaoExiste999")
    assert missing.status_code == 404


@pytest.mark.integration
def test_post_sem_nome_400(client):
    r = client.post("/api/players", json={})
    assert r.status_code == 400
