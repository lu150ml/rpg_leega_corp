"""Testes diretos do game_engine (sem HTTP)."""

from __future__ import annotations

import pytest

from app.db import repositories as repo
from app.services import game_engine

from tests.conftest import make_player


@pytest.mark.integration
def test_primeiro_evento_e_CS_D01_E1(app, client, db_conn):
    make_player(client, "p1")
    out = game_engine.proximo_evento_completo(db_conn, "p1")
    assert out["final"] is None
    assert out["evento"] is not None
    assert out["evento"]["id"] == "CS_D01_E1"


@pytest.mark.integration
def test_apos_decisao_avanca_para_CS_D01_E2(app, client, db_conn):
    make_player(client, "p2")
    assert game_engine.proximo_evento_completo(db_conn, "p2")["evento"]["id"] == "CS_D01_E1"

    game_engine.aplicar_decisao(db_conn, "p2", "CS_D01_E1", "opt_ok_CS_D01_E1_a")
    db_conn.commit()

    save = repo.get_save(db_conn, int(repo.get_player_by_name(db_conn, "p2")["id"]))
    assert save["evento_atual"] == "CS_D01_E2"
    flags = repo.save_row_to_api_dict(save)["flags"]
    assert flags.get("ok_CS_D01_E1") is True


@pytest.mark.integration
def test_tres_eventos_principais_avancam_dia(app, client, db_conn):
    make_player(client, "p3")
    pid = int(repo.get_player_by_name(db_conn, "p3")["id"])

    for eid, oid in [
        ("CS_D01_E1", "opt_ok_CS_D01_E1_a"),
        ("CS_D01_E2", "opt_ok_CS_D01_E2_a"),
        ("CS_D01_E3", "opt_ok_CS_D01_E3_a"),
    ]:
        game_engine.aplicar_decisao(db_conn, "p3", eid, oid)
        db_conn.commit()

    save = repo.get_save(db_conn, pid)
    assert int(save["dia_atual"]) == 2
    assert int(save["eventos_hoje"]) == 0


@pytest.mark.integration
def test_decisao_com_evento_errado_levanta(app, client, db_conn):
    make_player(client, "p4")
    with pytest.raises(ValueError, match="Evento"):
        game_engine.aplicar_decisao(db_conn, "p4", "CS_D02_E1", "opt_ok_CS_D02_E1_a")


@pytest.mark.integration
def test_partida_encerrada_nao_aceita_decisao(app, client, db_conn):
    make_player(client, "p5")
    pid = int(repo.get_player_by_name(db_conn, "p5")["id"])
    row = repo.get_save(db_conn, pid)
    flags = dict(repo.save_row_to_api_dict(row)["flags"])
    repo.update_save_full(
        db_conn,
        pid,
        evento_atual=None,
        energia=50,
        reputacao=50,
        networking=50,
        ansiedade=50,
        produtividade=50,
        aprendizado=50,
        dia_atual=1,
        eventos_hoje=0,
        flags=flags,
        final_obtido="funcionario_invisivel",
    )
    db_conn.commit()

    with pytest.raises(ValueError, match="encerrada"):
        game_engine.aplicar_decisao(db_conn, "p5", "CS_D01_E1", "opt_ok_CS_D01_E1_a")


@pytest.mark.integration
def test_colapso_demitido_no_proximo(app, client, db_conn):
    make_player(client, "p6")
    pid = int(repo.get_player_by_name(db_conn, "p6")["id"])
    row = repo.get_save(db_conn, pid)
    flags = dict(repo.save_row_to_api_dict(row)["flags"])
    repo.update_save_full(
        db_conn,
        pid,
        evento_atual="CS_D01_E1",
        energia=0,
        reputacao=50,
        networking=50,
        ansiedade=50,
        produtividade=50,
        aprendizado=50,
        dia_atual=1,
        eventos_hoje=0,
        flags=flags,
        final_obtido=None,
    )
    db_conn.commit()

    out = game_engine.proximo_evento_completo(db_conn, "p6")
    assert out.get("evento") is None
    assert out["final"]["id"] == "demitido"


@pytest.mark.integration
def test_colapso_burnout_no_proximo(app, client, db_conn):
    make_player(client, "p7")
    pid = int(repo.get_player_by_name(db_conn, "p7")["id"])
    row = repo.get_save(db_conn, pid)
    flags = dict(repo.save_row_to_api_dict(row)["flags"])
    repo.update_save_full(
        db_conn,
        pid,
        evento_atual="CS_D01_E1",
        energia=45,
        reputacao=50,
        networking=50,
        ansiedade=82,
        produtividade=50,
        aprendizado=50,
        dia_atual=1,
        eventos_hoje=0,
        flags=flags,
        final_obtido=None,
    )
    db_conn.commit()

    out = game_engine.proximo_evento_completo(db_conn, "p7")
    assert out.get("evento") is None
    assert out["final"]["id"] == "burnout"
