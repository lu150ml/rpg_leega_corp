"""Ranking global — somente leitura e listagem."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.db import get_db
from app.db import repositories as repo

ranking_bp = Blueprint("ranking", __name__, url_prefix="/api/ranking")


@ranking_bp.route("", methods=["GET"])
def get_ranking():
    """Devolve os melhores scores registrados (fim de partida)."""

    limite = request.args.get("limite", "20")
    try:
        n = max(1, min(100, int(limite)))
    except ValueError:
        n = 20

    db = get_db()
    itens = repo.ranking_top(db, n)
    return jsonify({"ranking": itens})
