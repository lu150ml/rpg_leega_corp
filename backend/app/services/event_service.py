"""Carrega e indexa eventos declarativos em backend/data/events/."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
_EVENTS_DIR = _BACKEND_ROOT / "data" / "events"


def events_dir() -> Path:
    return _EVENTS_DIR


@lru_cache(maxsize=1)
def _catalog() -> tuple[dict[str, dict[str, Any]], tuple[str, ...]]:
    index_path = _EVENTS_DIR / "index.json"
    with open(index_path, encoding="utf-8") as f:
        index = json.load(f)

    arquivos: list[str] = index.get("arquivos") or index.get("files") or []
    order: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}

    for nome_arquivo in arquivos:
        path = _EVENTS_DIR / nome_arquivo
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        eventos = data.get("eventos", data if isinstance(data, list) else [])
        for ev in eventos:
            eid = ev.get("id")
            if not eid:
                continue
            if eid in by_id:
                raise ValueError(f"ID de evento duplicado: {eid}")
            by_id[str(eid)] = ev
            order.append(str(eid))

    return by_id, tuple(order)


def get_event(event_id: str) -> dict[str, Any] | None:
    by_id, _ = _catalog()
    return by_id.get(event_id)


def iter_ordered_events() -> list[dict[str, Any]]:
    by_id, order = _catalog()
    return [by_id[eid] for eid in order if eid in by_id]


def ordered_event_ids() -> tuple[str, ...]:
    return _catalog()[1]


def catalog() -> tuple[dict[str, dict[str, Any]], tuple[str, ...]]:
    """Expõe o mapa id→evento e a ordem linear de `index.json` (somente leitura)."""

    return _catalog()
