"""Acesso ao banco — apenas SQL (fora das rotas)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_player_by_name(conn: sqlite3.Connection, nome: str) -> sqlite3.Row | None:
    cur = conn.execute("SELECT * FROM players WHERE nome = ?", (nome,))
    row = cur.fetchone()
    return row


def ensure_player_with_save(conn: sqlite3.Connection, nome: str) -> tuple[sqlite3.Row, bool]:
    """Garante jogador e save padrão; retorna (row_jogador, criado_agora)."""

    row = get_player_by_name(conn, nome)
    if row is not None:
        pid = int(row["id"])
        if get_save(conn, pid) is None:
            insert_default_save(conn, pid)
        return row, False

    insert_player(conn, nome)
    row2 = get_player_by_name(conn, nome)
    assert row2 is not None
    insert_default_save(conn, int(row2["id"]))
    return row2, True


def insert_player(conn: sqlite3.Connection, nome: str) -> int:
    cur = conn.execute("INSERT INTO players (nome) VALUES (?)", (nome,))
    return int(cur.lastrowid)


def get_save(conn: sqlite3.Connection, player_id: int) -> sqlite3.Row | None:
    cur = conn.execute("SELECT * FROM saves WHERE player_id = ?", (player_id,))
    return cur.fetchone()


def insert_default_save(conn: sqlite3.Connection, player_id: int) -> None:
    conn.execute(
        """
        INSERT INTO saves (
          player_id, evento_atual, energia, reputacao, networking, ansiedade,
          produtividade, aprendizado, dia_atual, eventos_hoje, flags_json,
          final_obtido, xp_total, cargo, rodada_no_conjunto, xp_conjunto, xp_rodada,
          atualizado_em
        )
        VALUES (?, NULL, 60, 5, 5, 0, 5, 5, 1, 0, '{}', NULL,
          0, 'trainee', 1, 0, 0, ?)
        """,
        (player_id, _utc_now_iso()),
    )


def update_save_full(
    conn: sqlite3.Connection,
    player_id: int,
    *,
    evento_atual: str | None,
    energia: int,
    reputacao: int,
    networking: int,
    ansiedade: int,
    produtividade: int,
    aprendizado: int,
    dia_atual: int,
    eventos_hoje: int,
    flags: dict[str, Any],
    final_obtido: str | None,
    xp_total: int,
    cargo: str,
    rodada_no_conjunto: int,
    xp_conjunto: int,
    xp_rodada: int,
) -> None:
    conn.execute(
        """
        UPDATE saves SET
          evento_atual = ?,
          energia = ?, reputacao = ?, networking = ?, ansiedade = ?,
          produtividade = ?, aprendizado = ?, dia_atual = ?, eventos_hoje = ?,
          flags_json = ?, final_obtido = ?,
          xp_total = ?, cargo = ?, rodada_no_conjunto = ?, xp_conjunto = ?, xp_rodada = ?,
          atualizado_em = ?
        WHERE player_id = ?
        """,
        (
            evento_atual,
            energia,
            reputacao,
            networking,
            ansiedade,
            produtividade,
            aprendizado,
            dia_atual,
            eventos_hoje,
            json.dumps(flags, ensure_ascii=False),
            final_obtido,
            xp_total,
            cargo,
            rodada_no_conjunto,
            xp_conjunto,
            xp_rodada,
            _utc_now_iso(),
            player_id,
        ),
    )


def save_row_to_api_dict(row: sqlite3.Row) -> dict[str, Any]:
    flags = json.loads(row["flags_json"])
    return {
        "player_id": row["player_id"],
        "evento_atual": row["evento_atual"],
        "energia": row["energia"],
        "reputacao": row["reputacao"],
        "networking": row["networking"],
        "ansiedade": row["ansiedade"],
        "produtividade": row["produtividade"],
        "aprendizado": row["aprendizado"],
        "dia_atual": row["dia_atual"],
        "eventos_hoje": row["eventos_hoje"],
        "flags": flags,
        "final_obtido": row["final_obtido"],
        "xp_total": row["xp_total"],
        "cargo": row["cargo"],
        "rodada_no_conjunto": row["rodada_no_conjunto"],
        "xp_conjunto": row["xp_conjunto"],
        "xp_rodada": row["xp_rodada"],
        "atualizado_em": row["atualizado_em"],
    }


def insert_decision(
    conn: sqlite3.Connection, player_id: int, evento_id: str, opcao_id: str
) -> None:
    conn.execute(
        """
        INSERT INTO decisions (player_id, evento_id, opcao_id)
        VALUES (?, ?, ?)
        """,
        (player_id, evento_id, opcao_id),
    )


def list_decisions(conn: sqlite3.Connection, player_id: int) -> list[dict[str, Any]]:
    cur = conn.execute(
        """
        SELECT evento_id, opcao_id, decidido_em
        FROM decisions WHERE player_id = ?
        ORDER BY id ASC
        """,
        (player_id,),
    )
    return [dict(r) for r in cur.fetchall()]


def update_save_evento_atual(
    conn: sqlite3.Connection, player_id: int, evento_atual: str | None
) -> None:
    """Alinha apenas o ponteiro de narrativa (ex.: reparo quando condições mudam)."""

    conn.execute(
        """
        UPDATE saves SET evento_atual = ?, atualizado_em = ?
        WHERE player_id = ?
        """,
        (evento_atual, _utc_now_iso(), player_id),
    )


def reset_save(conn: sqlite3.Connection, player_id: int) -> None:
    """Zera progresso da jornada e metadados de XP/cargo (reset completo)."""

    conn.execute("DELETE FROM decisions WHERE player_id = ?", (player_id,))
    conn.execute(
        """
        UPDATE saves SET
          evento_atual = NULL,
          energia = 60, reputacao = 5, networking = 5, ansiedade = 0,
          produtividade = 5, aprendizado = 5,
          dia_atual = 1, eventos_hoje = 0,
          flags_json = '{}', final_obtido = NULL,
          xp_total = 0, cargo = 'trainee', rodada_no_conjunto = 1,
          xp_conjunto = 0, xp_rodada = 0,
          atualizado_em = ?
        WHERE player_id = ?
        """,
        (_utc_now_iso(), player_id),
    )


def iniciar_nova_rodada(conn: sqlite3.Connection, player_id: int) -> None:
    """
    Nova run na mesma carreira: mantém xp_total e cargo; avança rodada;
    reseta narrativa e atributos. Exige partida encerrada (final_obtido preenchido).
    """

    conn.execute("DELETE FROM decisions WHERE player_id = ?", (player_id,))
    conn.execute(
        """
        UPDATE saves SET
          evento_atual = NULL,
          energia = 60, reputacao = 5, networking = 5, ansiedade = 0,
          produtividade = 5, aprendizado = 5,
          dia_atual = 1, eventos_hoje = 0,
          flags_json = '{}', final_obtido = NULL, xp_rodada = 0,
          rodada_no_conjunto = CASE
            WHEN rodada_no_conjunto >= 3 THEN 1
            ELSE rodada_no_conjunto + 1
          END,
          xp_conjunto = CASE
            WHEN rodada_no_conjunto >= 3 THEN 0
            ELSE xp_conjunto
          END,
          atualizado_em = ?
        WHERE player_id = ?
        """,
        (_utc_now_iso(), player_id),
    )


def insert_ranking_entry(
    conn: sqlite3.Connection,
    player_id: int,
    nome: str,
    pontuacao: int,
    final_id: str,
) -> int:
    """Insere registro de fim de jogo e devolve o id da linha."""

    cur = conn.execute(
        """
        INSERT INTO ranking_global (player_id, nome, pontuacao, final_id, registrado_em)
        VALUES (?, ?, ?, ?, ?)
        """,
        (player_id, nome, pontuacao, final_id, _utc_now_iso()),
    )
    return int(cur.lastrowid)


def contar_melhor_pontuacao(conn: sqlite3.Connection, pontuacao: int) -> int:
    """Quantidade de entradas estritamente acima desta pontuação (+1 = posição)."""

    cur = conn.execute(
        "SELECT COUNT(*) FROM ranking_global WHERE pontuacao > ?",
        (pontuacao,),
    )
    row = cur.fetchone()
    return int(row[0]) if row else 0


def ultima_entrada_ranking_jogador(
    conn: sqlite3.Connection, player_id: int
) -> sqlite3.Row | None:
    """Última partida concluída registrada no ranking (mais recente por id)."""

    cur = conn.execute(
        """
        SELECT * FROM ranking_global
        WHERE player_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (player_id,),
    )
    return cur.fetchone()


def ranking_top(conn: sqlite3.Connection, limite: int = 20) -> list[dict[str, Any]]:
    cur = conn.execute(
        """
        SELECT nome, pontuacao, final_id, registrado_em
        FROM ranking_global
        ORDER BY pontuacao DESC, registrado_em ASC
        LIMIT ?
        """,
        (limite,),
    )
    return [dict(r) for r in cur.fetchall()]
