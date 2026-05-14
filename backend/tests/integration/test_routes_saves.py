"""Rotas /api/saves."""

from __future__ import annotations

import pytest

from tests.conftest import make_player


@pytest.mark.integration
def test_get_save_200(client):
    make_player(client, "Savetest")
    r = client.get("/api/saves/Savetest")
    assert r.status_code == 200
    body = r.get_json()
    assert body["energia"] == 70
    assert body["flags"] == {}


@pytest.mark.integration
def test_get_save_404(client):
    r = client.get("/api/saves/FulanoInexistente")
    assert r.status_code == 404


@pytest.mark.integration
def test_put_save_atualiza_campo(client):
    make_player(client, "Putuser")
    r = client.put(
        "/api/saves/Putuser",
        json={"energia": 55},
    )
    assert r.status_code == 200
    assert r.get_json()["energia"] == 55


@pytest.mark.integration
def test_delete_reset_save(client):
    make_player(client, "Resetuser")
    client.put("/api/saves/Resetuser", json={"energia": 10})
    del_r = client.delete("/api/saves/Resetuser")
    assert del_r.status_code == 204
    get_r = client.get("/api/saves/Resetuser")
    assert get_r.get_json()["energia"] == 70
