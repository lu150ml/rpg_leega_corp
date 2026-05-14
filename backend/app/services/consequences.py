"""Handlers de consequências ao escolher opções (extensível por tipo)."""

from __future__ import annotations

from typing import Any, Callable

ATTRIBUTE_KEYS = frozenset(
    {
        "energia",
        "reputacao",
        "networking",
        "ansiedade",
        "produtividade",
        "aprendizado",
    }
)

ConsequenceHandler = Callable[[dict[str, Any], dict[str, Any], dict[str, int]], None]


def set_flag(con: dict[str, Any], flags: dict[str, Any], _attrs: dict[str, int]) -> None:
    chave = str(con.get("chave", ""))
    flags[chave] = con.get("valor")


def alterar_atributo(
    con: dict[str, Any], _flags: dict[str, Any], attrs: dict[str, int]
) -> None:
    chave = str(con.get("chave", ""))
    if chave not in ATTRIBUTE_KEYS:
        return
    delta = int(con.get("delta", 0))
    attrs[chave] = attrs[chave] + delta


CONSEQUENCE_HANDLERS: dict[str, ConsequenceHandler] = {
    "set_flag": set_flag,
    "alterar_atributo": alterar_atributo,
}


def aplicar_consequencias(
    consequencias: list[dict[str, Any]], flags: dict[str, Any], attrs: dict[str, int]
) -> None:
    for con in consequencias:
        tipo = con.get("tipo")
        if tipo not in CONSEQUENCE_HANDLERS:
            raise KeyError(f"Tipo de consequência desconhecido: {tipo}")
        CONSEQUENCE_HANDLERS[tipo](con, flags, attrs)


def clamp_attrs(attrs: dict[str, int]) -> None:
    for k in ATTRIBUTE_KEYS:
        v = attrs[k]
        attrs[k] = max(0, min(100, v))
