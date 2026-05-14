"""Orquestra elegibilidade de eventos e aplicação de decisões."""

from __future__ import annotations

import sqlite3
from typing import Any

from app.db import repositories as repo
from app.services import cargo, conditions, consequences, endings, event_service, scoring

_CHAVES_PONTUACAO = (
    "energia",
    "reputacao",
    "networking",
    "ansiedade",
    "produtividade",
    "aprendizado",
)


def _attrs_para_pontuacao(attrs: dict[str, Any]) -> dict[str, int]:
    return {k: int(attrs[k]) for k in _CHAVES_PONTUACAO}


def _payload_fim_de_jogo(
    conn: sqlite3.Connection,
    player_id: int,
    nome_jogador: str,
    save_api: dict[str, Any],
    attrs: dict[str, Any],
    final_id: str,
    meta_progressao: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resposta padrão ao encerrar partida (ranking + final)."""

    pontuacao = scoring.calcular_pontuacao(_attrs_para_pontuacao(attrs))
    repo.insert_ranking_entry(conn, player_id, nome_jogador, pontuacao, final_id)
    posicao = repo.contar_melhor_pontuacao(conn, pontuacao) + 1
    topo = repo.ranking_top(conn, 15)
    out: dict[str, Any] = {
        "save": save_api,
        "proximo_evento": None,
        "final": endings.final_para_resposta(final_id),
        "pontuacao": pontuacao,
        "posicao_ranking": posicao,
        "ranking_top": topo,
    }
    if meta_progressao is not None:
        out["meta_progressao"] = meta_progressao
    return out


def _attrs_from_save(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "energia": int(row["energia"]),
        "reputacao": int(row["reputacao"]),
        "networking": int(row["networking"]),
        "ansiedade": int(row["ansiedade"]),
        "produtividade": int(row["produtividade"]),
        "aprendizado": int(row["aprendizado"]),
        "xp": int(row["xp_rodada"]),
    }


def _resolve_proximo_id(conn: sqlite3.Connection, save: sqlite3.Row) -> str | None:
    if save["final_obtido"]:
        return None

    flags: dict[str, Any] = dict(repo.save_row_to_api_dict(save)["flags"])
    attrs = _attrs_from_save(save)
    ordem = event_service.ordered_event_ids()
    by_id, _ = event_service.catalog()

    atual = save["evento_atual"]
    if atual:
        ev = by_id.get(str(atual))
        if ev and conditions.avaliar_condicoes(
            ev.get("condicoes") or [], flags, attrs
        ):
            return str(atual)

    for eid in ordem:
        ev = by_id[eid]
        if conditions.avaliar_condicoes(ev.get("condicoes") or [], flags, attrs):
            return eid
    return None


def proximo_evento_completo(conn: sqlite3.Connection, nome: str) -> dict[str, Any]:
    """Retorna payload para GET /api/events/proximo."""

    p = repo.get_player_by_name(conn, nome)
    if not p:
        raise ValueError("Jogador não encontrado")

    player_id = int(p["id"])
    save = repo.get_save(conn, player_id)
    if not save:
        raise ValueError("Save não encontrado")

    if save["final_obtido"]:
        fid = str(save["final_obtido"])
        attrs = _attrs_from_save(save)
        ultima = repo.ultima_entrada_ranking_jogador(conn, player_id)
        if ultima is not None:
            pontuacao = int(ultima["pontuacao"])
        else:
            pontuacao = scoring.calcular_pontuacao(_attrs_para_pontuacao(attrs))
        posicao = repo.contar_melhor_pontuacao(conn, pontuacao) + 1
        topo = repo.ranking_top(conn, 15)
        return {
            "evento": None,
            "final": endings.final_para_resposta(fid),
            "pontuacao": pontuacao,
            "posicao_ranking": posicao,
            "ranking_top": topo,
        }

    attrs_vivos = _attrs_from_save(save)
    flags = dict(repo.save_row_to_api_dict(save)["flags"])
    colapso = endings.final_por_colapso_imediato(attrs_vivos, flags)
    if colapso:
        xp_rodada_atual = int(save["xp_rodada"])
        bonus = cargo.calcular_xp_por_final(colapso)
        xp_run = xp_rodada_atual + bonus
        xp_total = int(save["xp_total"]) + xp_run
        xp_conjunto = int(save["xp_conjunto"]) + xp_run
        novo_cargo = cargo.calcular_cargo(xp_total)

        repo.update_save_full(
            conn,
            player_id,
            evento_atual=None,
            energia=int(attrs_vivos["energia"]),
            reputacao=int(attrs_vivos["reputacao"]),
            networking=int(attrs_vivos["networking"]),
            ansiedade=int(attrs_vivos["ansiedade"]),
            produtividade=int(attrs_vivos["produtividade"]),
            aprendizado=int(attrs_vivos["aprendizado"]),
            dia_atual=int(save["dia_atual"]),
            eventos_hoje=int(save["eventos_hoje"]),
            flags=flags,
            final_obtido=colapso,
            xp_total=xp_total,
            cargo=novo_cargo,
            rodada_no_conjunto=int(save["rodada_no_conjunto"]),
            xp_conjunto=xp_conjunto,
            xp_rodada=0,
        )
        save2 = repo.get_save(conn, player_id)
        assert save2 is not None
        save_api = repo.save_row_to_api_dict(save2)
        nome_j = str(p["nome"])
        meta = {
            "xp_ganho_nesta_run": xp_run,
            "xp_bonus_final": bonus,
            "xp_total": xp_total,
            "cargo": novo_cargo,
            "rodada_no_conjunto": int(save["rodada_no_conjunto"]),
            "xp_conjunto": xp_conjunto,
        }
        out = _payload_fim_de_jogo(
            conn,
            player_id,
            nome_j,
            save_api,
            attrs_vivos,
            colapso,
            meta_progressao=meta,
        )
        conn.commit()
        return out

    eid = _resolve_proximo_id(conn, save)
    atual_ptr = save["evento_atual"]
    if (
        eid is not None
        and atual_ptr is not None
        and str(atual_ptr) != str(eid)
    ):
        repo.update_save_evento_atual(conn, player_id, eid)
        conn.commit()
        save = repo.get_save(conn, player_id)
        assert save is not None

    if not eid:
        return {"evento": None, "final": None}

    ev = event_service.get_event(eid)
    return {"evento": ev, "final": None}


def aplicar_decisao(
    conn: sqlite3.Connection, nome: str, evento_id: str, opcao_id: str
) -> dict[str, Any]:
    """Persiste decisão, aplica efeitos e devolve save + próximo ou final."""

    p = repo.get_player_by_name(conn, nome)
    if not p:
        raise ValueError("Jogador não encontrado")
    player_id = int(p["id"])
    save_row = repo.get_save(conn, player_id)
    if not save_row:
        raise ValueError("Save não encontrado")

    if save_row["final_obtido"]:
        raise ValueError("Partida já encerrada")

    esperado_id = _resolve_proximo_id(conn, save_row)
    atual = save_row["evento_atual"]
    if esperado_id is not None and atual is not None and str(atual) != str(esperado_id):
        repo.update_save_evento_atual(conn, player_id, esperado_id)
        conn.commit()
        save_row = repo.get_save(conn, player_id)
        assert save_row is not None

    esperado_id = _resolve_proximo_id(conn, save_row)
    atual = save_row["evento_atual"]
    if atual:
        if str(atual) != str(evento_id):
            raise ValueError("Evento atual divergente do save")
    elif esperado_id != str(evento_id):
        raise ValueError("Evento inválido para o progresso atual")

    ev = event_service.get_event(evento_id)
    if not ev:
        raise ValueError("Evento desconhecido")

    opcao = next(
        (o for o in ev.get("opcoes", []) if str(o.get("id")) == str(opcao_id)), None
    )
    if not opcao:
        raise ValueError("Opção inválida para o evento")

    flags = dict(repo.save_row_to_api_dict(save_row)["flags"])
    attrs = _attrs_from_save(save_row)
    consequences.aplicar_consequencias(opcao.get("consequencias") or [], flags, attrs)
    consequences.clamp_attrs(attrs)

    dia_atual = int(save_row["dia_atual"])
    eventos_hoje = int(save_row["eventos_hoje"])
    if ev.get("evento_principal", True):
        eventos_hoje += 1
        if eventos_hoje >= 3:
            eventos_hoje = 0
            dia_atual = min(5, dia_atual + 1)

    colapso = endings.final_por_colapso_imediato(attrs, flags)
    if colapso:
        final_id: str | None = colapso
        evento_atual = None
    else:
        proximo = opcao.get("proximo_evento")
        if proximo is not None and proximo != "":
            final_id = None
            evento_atual = str(proximo)
        else:
            final_id = endings.calcular_final_id(attrs, flags)
            evento_atual = None

    xp_rodada_after = int(attrs.get("xp", 0))
    bonus = 0
    xp_run = 0
    if final_id:
        bonus = cargo.calcular_xp_por_final(final_id)
        xp_run = xp_rodada_after + bonus
        xp_total = int(save_row["xp_total"]) + xp_run
        xp_conjunto = int(save_row["xp_conjunto"]) + xp_run
        novo_cargo = cargo.calcular_cargo(xp_total)
        xp_rodada_persist = 0
    else:
        xp_total = int(save_row["xp_total"])
        xp_conjunto = int(save_row["xp_conjunto"])
        novo_cargo = str(save_row["cargo"])
        xp_rodada_persist = xp_rodada_after

    repo.update_save_full(
        conn,
        player_id,
        evento_atual=evento_atual,
        energia=int(attrs["energia"]),
        reputacao=int(attrs["reputacao"]),
        networking=int(attrs["networking"]),
        ansiedade=int(attrs["ansiedade"]),
        produtividade=int(attrs["produtividade"]),
        aprendizado=int(attrs["aprendizado"]),
        dia_atual=dia_atual,
        eventos_hoje=eventos_hoje,
        flags=flags,
        final_obtido=final_id,
        xp_total=xp_total,
        cargo=novo_cargo,
        rodada_no_conjunto=int(save_row["rodada_no_conjunto"]),
        xp_conjunto=xp_conjunto,
        xp_rodada=xp_rodada_persist,
    )
    repo.insert_decision(conn, player_id, evento_id, opcao_id)

    save_atualizado = repo.get_save(conn, player_id)
    assert save_atualizado is not None
    save_api = repo.save_row_to_api_dict(save_atualizado)

    if final_id:
        nome_jogador = str(p["nome"])
        meta = {
            "xp_ganho_nesta_run": xp_run,
            "xp_bonus_final": bonus,
            "xp_total": xp_total,
            "cargo": novo_cargo,
            "rodada_no_conjunto": int(save_row["rodada_no_conjunto"]),
            "xp_conjunto": xp_conjunto,
        }
        return _payload_fim_de_jogo(
            conn,
            player_id,
            nome_jogador,
            save_api,
            attrs,
            final_id,
            meta_progressao=meta,
        )

    prox = event_service.get_event(evento_atual) if evento_atual else None
    return {"save": save_api, "proximo_evento": prox, "final": None}
