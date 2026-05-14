"""Persistência de save por nome do jogador."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request

from app.db import get_db
from app.db import repositories as repo

saves_bp = Blueprint("saves", __name__, url_prefix="/api/saves")


@saves_bp.route("/<path:nome>", methods=["GET"])
def get_save(nome: str):
    db = get_db()
    p = repo.get_player_by_name(db, nome)
    if not p:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    s = repo.get_save(db, int(p["id"]))
    if not s:
        return jsonify({"erro": "Save não encontrado"}), 404
    return jsonify(repo.save_row_to_api_dict(s))


@saves_bp.route("/<path:nome>", methods=["PUT"])
def put_save(nome: str):
    db = get_db()
    p = repo.get_player_by_name(db, nome)
    if not p:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    s = repo.get_save(db, int(p["id"]))
    if not s:
        return jsonify({"erro": "Save não encontrado"}), 404

    data = request.get_json(silent=True) or {}
    base = repo.save_row_to_api_dict(s)

    allowed = {
        "evento_atual",
        "energia",
        "reputacao",
        "networking",
        "ansiedade",
        "produtividade",
        "aprendizado",
        "dia_atual",
        "eventos_hoje",
        "flags",
        "final_obtido",
    }
    for k in allowed:
        if k in data:
            base[k] = data[k]

    if not isinstance(base["flags"], dict):
        return jsonify({"erro": "'flags' deve ser um objeto"}), 400

    try:
        repo.update_save_full(
            db,
            int(p["id"]),
            evento_atual=base["evento_atual"],
            energia=int(base["energia"]),
            reputacao=int(base["reputacao"]),
            networking=int(base["networking"]),
            ansiedade=int(base["ansiedade"]),
            produtividade=int(base["produtividade"]),
            aprendizado=int(base["aprendizado"]),
            dia_atual=int(base["dia_atual"]),
            eventos_hoje=int(base["eventos_hoje"]),
            flags=dict(base["flags"]),
            final_obtido=base.get("final_obtido"),
        )
    except (TypeError, ValueError):
        return jsonify({"erro": "Valores numéricos inválidos"}), 400

    db.commit()
    atualizado = repo.get_save(db, int(p["id"]))
    assert atualizado is not None
    return jsonify(repo.save_row_to_api_dict(atualizado))


@saves_bp.route("/<path:nome>", methods=["DELETE"])
def delete_save(nome: str):
    db = get_db()
    p = repo.get_player_by_name(db, nome)
    if not p:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    s = repo.get_save(db, int(p["id"]))
    if not s:
        return jsonify({"erro": "Save não encontrado"}), 404
    repo.reset_save(db, int(p["id"]))
    db.commit()
    return ("", 204)
