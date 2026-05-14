"""Handlers de condições de elegibilidade de eventos (extensível por tipo)."""

from __future__ import annotations

from typing import Any, Callable

ConditionHandler = Callable[[dict[str, Any], dict[str, Any], dict[str, int]], bool]


def flag_ausente(
    cond: dict[str, Any], flags: dict[str, Any], _attrs: dict[str, int]
) -> bool:
    chave = str(cond.get("chave", ""))
    if chave not in flags:
        return True
    return not bool(flags[chave])


def flag_presente(
    cond: dict[str, Any], flags: dict[str, Any], _attrs: dict[str, int]
) -> bool:
    chave = str(cond.get("chave", ""))
    return bool(flags.get(chave))


def atributo_min(
    cond: dict[str, Any], _flags: dict[str, Any], attrs: dict[str, int]
) -> bool:
    chave = str(cond.get("chave", ""))
    valor = int(cond.get("valor", 0))
    return int(attrs.get(chave, 0)) >= valor


def atributo_max(
    cond: dict[str, Any], _flags: dict[str, Any], attrs: dict[str, int]
) -> bool:
    chave = str(cond.get("chave", ""))
    valor = int(cond.get("valor", 100))
    return int(attrs.get(chave, 0)) <= valor


CONDITION_HANDLERS: dict[str, ConditionHandler] = {
    "flag_ausente": flag_ausente,
    "flag_presente": flag_presente,
    "atributo_min": atributo_min,
    "atributo_max": atributo_max,
}


def avaliar_condicoes(
    condicoes: list[dict[str, Any]], flags: dict[str, Any], attrs: dict[str, int]
) -> bool:
    for cond in condicoes:
        tipo = cond.get("tipo")
        if tipo not in CONDITION_HANDLERS:
            raise KeyError(f"Tipo de condição desconhecido: {tipo}")
        if not CONDITION_HANDLERS[tipo](cond, flags, attrs):
            return False
    return True
