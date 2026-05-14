"""Factory Flask + estáticos do frontend."""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

from app.db import init_db
from app.routes import decisions_bp, events_bp, players_bp, ranking_bp, saves_bp

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = _BACKEND_ROOT.parent
_FRONTEND_DIR = _PROJECT_ROOT / "frontend"


def create_app() -> Flask:
    """Cria e configura a aplicação."""

    app = Flask(
        __name__,
        static_folder=str(_FRONTEND_DIR),
        static_url_path="",
    )

    default_db = _BACKEND_ROOT / "game.db"
    app.config.from_mapping(
        DATABASE_PATH=os.environ.get("DATABASE_PATH", str(default_db)),
    )

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    init_db(app)

    app.register_blueprint(players_bp)
    app.register_blueprint(saves_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(ranking_bp)
    app.register_blueprint(decisions_bp)

    @app.get("/")
    def _root():
        return send_from_directory(str(_FRONTEND_DIR), "index.html")

    return app
