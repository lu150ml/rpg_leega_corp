"""Pacote de blueprints da API."""

from .decisions import decisions_bp
from .events import events_bp
from .players import players_bp
from .ranking import ranking_bp
from .saves import saves_bp

__all__ = ["decisions_bp", "events_bp", "players_bp", "ranking_bp", "saves_bp"]
