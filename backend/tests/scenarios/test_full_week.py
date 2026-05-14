"""Simulações de partida completa e perfis extremos."""

from __future__ import annotations

import pytest

from app.db import repositories as repo
from app.services import game_engine

from tests.conftest import make_player


def _primeira_opcao_id(ev: dict) -> str:
    return str(ev["opcoes"][0]["id"])


def _pick_alto_desempenho(ev: dict) -> str:
    """Maximiza prod/rep/ap com leve penalidade por ansiedade."""

    def score(op: dict) -> float:
        s = 0.0
        for c in op.get("consequencias", []):
            if c.get("tipo") != "alterar_atributo":
                continue
            k = str(c.get("chave", ""))
            d = int(c.get("delta", 0))
            if k in ("produtividade", "reputacao", "aprendizado"):
                s += d
            elif k == "ansiedade":
                s -= 0.5 * d
            elif k == "energia":
                s += 0.2 * d
        return s

    return str(max(ev["opcoes"], key=score)["id"])


def _pick_burnout(ev: dict) -> str:
    """Favorece +ansiedade e -energia."""

    def score(op: dict) -> float:
        an = en = 0
        for c in op.get("consequencias", []):
            if c.get("tipo") != "alterar_atributo":
                continue
            if str(c.get("chave")) == "ansiedade":
                an += int(c.get("delta", 0))
            if str(c.get("chave")) == "energia":
                en += int(c.get("delta", 0))
        return 2.0 * an - en

    return str(max(ev["opcoes"], key=score)["id"])


@pytest.mark.scenario
def test_semana_completa_primeira_opcao(app, client, db_conn):
    make_player(client, "SemanaA")
    res_final = None
    for _ in range(15):
        payload = game_engine.proximo_evento_completo(db_conn, "SemanaA")
        if payload.get("final"):
            res_final = payload
            break
        ev = payload["evento"]
        assert ev is not None
        res = game_engine.aplicar_decisao(
            db_conn, "SemanaA", ev["id"], _primeira_opcao_id(ev)
        )
        db_conn.commit()
        if res.get("final"):
            res_final = res
            break
    assert res_final is not None
    assert res_final["final"]["id"]
    pid = int(repo.get_player_by_name(db_conn, "SemanaA")["id"])
    save = repo.get_save(db_conn, pid)
    assert int(save["dia_atual"]) == 5
    assert save["final_obtido"]


@pytest.mark.scenario
def test_caminho_alto_desempenho(app, client, db_conn):
    make_player(client, "HighPerf")
    res = None
    for _ in range(15):
        payload = game_engine.proximo_evento_completo(db_conn, "HighPerf")
        if payload.get("final"):
            res = payload
            break
        ev = payload["evento"]
        oid = _pick_alto_desempenho(ev)
        res = game_engine.aplicar_decisao(db_conn, "HighPerf", ev["id"], oid)
        db_conn.commit()
        if res.get("final"):
            break
    assert res and res.get("final")
    assert res["final"]["id"] in ("trainee_lenda", "promessa_corporativa")


@pytest.mark.scenario
def test_caminho_pressao_burnout_ou_demissao(app, client, db_conn):
    make_player(client, "Burn")
    steps = 0
    res = None
    while steps < 30:
        payload = game_engine.proximo_evento_completo(db_conn, "Burn")
        if payload.get("final"):
            res = payload
            break
        ev = payload.get("evento")
        if ev is None:
            break
        oid = _pick_burnout(ev)
        res = game_engine.aplicar_decisao(db_conn, "Burn", ev["id"], oid)
        db_conn.commit()
        steps += 1
        if res.get("final"):
            break
    assert res and res.get("final")
    assert res["final"]["id"] in ("burnout", "demitido")
    assert steps < 15
