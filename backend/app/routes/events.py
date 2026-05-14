"""Leitura de eventos e resolução do próximo elegível."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.db import get_db
from app.db import repositories as repo
from app.services import event_service, game_engine

events_bp = Blueprint("events", __name__, url_prefix="/api/events")


@events_bp.route("/proximo", methods=["GET"])
def get_proximo():
    nome = request.args.get("nome", "").strip()
    if not nome:
        return jsonify({"erro": "Query 'nome' é obrigatória"}), 400

    db = get_db()
    try:
        payload = game_engine.proximo_evento_completo(db, nome)
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404
    return jsonify(payload)


@events_bp.route("/<event_id>", methods=["GET"])
def get_evento(event_id: str):
    ev = event_service.get_event(event_id)
    if not ev:
        return jsonify({"erro": "Evento não encontrado"}), 404
    return jsonify(ev)
