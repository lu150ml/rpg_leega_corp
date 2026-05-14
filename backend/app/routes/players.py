"""Rotas HTTP — apenas validação e delegação."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.db import get_db
from app.db import repositories as repo

players_bp = Blueprint("players", __name__, url_prefix="/api/players")


def _normalize_nome(raw: str | None) -> str:
    if raw is None:
        return ""
    return str(raw).strip()


@players_bp.route("", methods=["POST"])
def post_player():
    """Cria jogador ou retorna existente."""

    data = request.get_json(silent=True) or {}
    nome = _normalize_nome(data.get("nome"))
    if not nome:
        return jsonify({"erro": "Campo 'nome' é obrigatório"}), 400

    db = get_db()
    row, criado = repo.ensure_player_with_save(db, nome)
    db.commit()
    status = 201 if criado else 200
    return (
        jsonify(
            {
                "id": int(row["id"]),
                "nome": row["nome"],
                "criado_em": row["criado_em"],
            }
        ),
        status,
    )


@players_bp.route("/<path:nome>", methods=["GET"])
def get_player(nome: str):
    db = get_db()
    row = repo.get_player_by_name(db, nome)
    if not row:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    return jsonify(
        {
            "id": int(row["id"]),
            "nome": row["nome"],
            "criado_em": row["criado_em"],
        }
    )
