"""Rotas /api/ranking."""

from __future__ import annotations

import pytest


@pytest.mark.integration
def test_ranking_lista_vazia(client):
    r = client.get("/api/ranking")
    assert r.status_code == 200
    assert r.get_json() == {"ranking": []}


@pytest.mark.integration
def test_ranking_limite(client):
    r = client.get("/api/ranking?limite=5")
    assert r.status_code == 200
    assert "ranking" in r.get_json()
