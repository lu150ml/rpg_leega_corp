"""Conexão SQLite com Row factory e chaves estrangeiras ativas."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import flask

from app.db import migrations


def init_app(app: flask.Flask) -> None:
    """Registra abertura/fechamento de conexão por requisição e aplica schema."""

    db_path = Path(app.config["DATABASE_PATH"]).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    schema_path = Path(__file__).with_name("schema.sql")
    with open(schema_path, encoding="utf-8") as f:
        schema_sql = f.read()

    conn_init = sqlite3.connect(str(db_path))
    try:
        conn_init.execute("PRAGMA foreign_keys = ON")
        conn_init.executescript(schema_sql)
        migrations.apply_saves_corporate_survivor_attrs(conn_init)
        migrations.ensure_progresso_e_ranking(conn_init)
        conn_init.commit()
    finally:
        conn_init.close()

    def _get_db() -> sqlite3.Connection:
        if "db" not in flask.g:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            flask.g.db = conn
        return flask.g.db

    @app.teardown_appcontext
    def _close_db(_exc: BaseException | None) -> None:
        conn: sqlite3.Connection | None = flask.g.pop("db", None)
        if conn is not None:
            conn.close()

    app.get_db = _get_db  # type: ignore[attr-defined]


def get_db() -> sqlite3.Connection:
    """Retorna a conexão da requisição atual."""

    return flask.current_app.get_db()  # type: ignore[attr-defined]
