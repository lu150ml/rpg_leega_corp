"""Registro de decisões e histórico."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.db import get_db
from app.db import repositories as repo
from app.services import game_engine

decisions_bp = Blueprint("decisions", __name__, url_prefix="/api/decisions")


@decisions_bp.route("", methods=["POST"])
def post_decision():
    data = request.get_json(silent=True) or {}
    nome = str(data.get("nome", "")).strip()
    evento_id = str(data.get("evento_id", "")).strip()
    opcao_id = str(data.get("opcao_id", "")).strip()
    if not nome or not evento_id or not opcao_id:
        return (
            jsonify(
                {
                    "erro": "Campos 'nome', 'evento_id' e 'opcao_id' são obrigatórios",
                }
            ),
            400,
        )

    db = get_db()
    try:
        resultado = game_engine.aplicar_decisao(db, nome, evento_id, opcao_id)
        db.commit()
    except ValueError as e:
        db.rollback()
        return jsonify({"erro": str(e)}), 400
    return jsonify(resultado)


@decisions_bp.route("/<path:nome>", methods=["GET"])
def list_decisions(nome: str):
    db = get_db()
    p = repo.get_player_by_name(db, nome)
    if not p:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    itens = repo.list_decisions(db, int(p["id"]))
    return jsonify({"decisoes": itens})
