"""Camada de persistência SQLite."""

from .connection import get_db, init_app as init_db

__all__ = ["get_db", "init_db"]
