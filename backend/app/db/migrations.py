"""Migrações leves de schema SQLite (sem Alembic)."""

from __future__ import annotations

import sqlite3


def apply_saves_corporate_survivor_attrs(conn: sqlite3.Connection) -> None:
    """
    Converte colunas antigas (incl. conhecimento_tecnico / estresse) para o modelo
    Corporate Survivor: energia, ansiedade, aprendizado.
    """

    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='saves'"
    )
    if cur.fetchone() is None:
        return

    cols = {row[1] for row in conn.execute("PRAGMA table_info(saves)")}
    if "energia" in cols:
        return

    if "produtividade" not in cols:
        return

    conn.executescript(
        """
        CREATE TABLE saves_cs (
          player_id INTEGER PRIMARY KEY,
          evento_atual TEXT,
          energia INTEGER NOT NULL DEFAULT 70,
          reputacao INTEGER NOT NULL DEFAULT 50,
          networking INTEGER NOT NULL DEFAULT 50,
          ansiedade INTEGER NOT NULL DEFAULT 0,
          produtividade INTEGER NOT NULL DEFAULT 50,
          aprendizado INTEGER NOT NULL DEFAULT 50,
          dia_atual INTEGER NOT NULL DEFAULT 1,
          eventos_hoje INTEGER NOT NULL DEFAULT 0,
          flags_json TEXT NOT NULL DEFAULT '{}',
          final_obtido TEXT,
          atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
        );

        INSERT INTO saves_cs (
          player_id, evento_atual, energia, reputacao, networking, ansiedade,
          produtividade, aprendizado, dia_atual, eventos_hoje, flags_json, final_obtido, atualizado_em
        )
        SELECT
          player_id,
          evento_atual,
          70,
          reputacao,
          networking,
          estresse,
          produtividade,
          conhecimento_tecnico,
          1,
          0,
          flags_json,
          final_obtido,
          atualizado_em
        FROM saves;

        DROP TABLE saves;
        ALTER TABLE saves_cs RENAME TO saves;
        """
    )


def ensure_progresso_e_ranking(conn: sqlite3.Connection) -> None:
    """Adiciona colunas de progresso semanal e tabela de ranking em bancos legados."""

    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='saves'"
    )
    if cur.fetchone() is not None:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(saves)")}
        if "dia_atual" not in cols:
            conn.execute(
                "ALTER TABLE saves ADD COLUMN dia_atual INTEGER NOT NULL DEFAULT 1"
            )
        if "eventos_hoje" not in cols:
            conn.execute(
                "ALTER TABLE saves ADD COLUMN eventos_hoje INTEGER NOT NULL DEFAULT 0"
            )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ranking_global (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          player_id INTEGER NOT NULL,
          nome TEXT NOT NULL,
          pontuacao INTEGER NOT NULL,
          final_id TEXT NOT NULL,
          registrado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ranking_pontuacao
        ON ranking_global (pontuacao DESC)
        """
    )


def ensure_cargo_e_rodadas(conn: sqlite3.Connection) -> None:
    """Adiciona colunas de XP, cargo e rodadas em bancos legados."""

    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='saves'"
    )
    if cur.fetchone() is None:
        return

    cols = {row[1] for row in conn.execute("PRAGMA table_info(saves)")}
    if "xp_total" not in cols:
        conn.execute(
            "ALTER TABLE saves ADD COLUMN xp_total INTEGER NOT NULL DEFAULT 0"
        )
    if "cargo" not in cols:
        conn.execute(
            "ALTER TABLE saves ADD COLUMN cargo TEXT NOT NULL DEFAULT 'trainee'"
        )
    if "rodada_no_conjunto" not in cols:
        conn.execute(
            "ALTER TABLE saves ADD COLUMN rodada_no_conjunto INTEGER NOT NULL DEFAULT 1"
        )
    if "xp_conjunto" not in cols:
        conn.execute(
            "ALTER TABLE saves ADD COLUMN xp_conjunto INTEGER NOT NULL DEFAULT 0"
        )
    if "xp_rodada" not in cols:
        conn.execute(
            "ALTER TABLE saves ADD COLUMN xp_rodada INTEGER NOT NULL DEFAULT 0"
        )
