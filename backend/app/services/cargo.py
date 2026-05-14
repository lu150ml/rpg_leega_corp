"""Progressão de cargo (XP total) configurável em data/cargo.json."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
_CARGO_PATH = _BACKEND_ROOT / "data" / "cargo.json"


@lru_cache(maxsize=1)
def _cargo_payload() -> dict[str, Any]:
    with open(_CARGO_PATH, encoding="utf-8") as f:
        return json.load(f)


def calcular_cargo(xp_total: int) -> str:
    """Retorna o id do cargo mais alto possível para o XP total."""

    cargos: list[dict[str, Any]] = sorted(
        _cargo_payload().get("cargos", []),
        key=lambda c: int(c.get("xp_minimo", 0)),
    )
    atual = str(cargos[0]["id"]) if cargos else "trainee"
    for c in cargos:
        if int(xp_total) >= int(c.get("xp_minimo", 0)):
            atual = str(c["id"])
    return atual


def calcular_xp_por_final(final_id: str) -> int:
    """Bônus de XP ao encerrar a run com um determinado final."""

    tabela: dict[str, Any] = _cargo_payload().get("xp_por_final", {})
    return int(tabela.get(final_id, 0))
