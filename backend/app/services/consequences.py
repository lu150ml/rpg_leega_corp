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

ConsequenceHandler = Callable[
    [dict[str, Any], dict[str, Any], dict[str, Any]], None
]


def set_flag(con: dict[str, Any], flags: dict[str, Any], _attrs: dict[str, Any]) -> None:
    chave = str(con.get("chave", ""))
    flags[chave] = con.get("valor")


def alterar_atributo(
    con: dict[str, Any], _flags: dict[str, Any], attrs: dict[str, Any]
) -> None:
    chave = str(con.get("chave", ""))
    if chave not in ATTRIBUTE_KEYS:
        return
    delta = int(con.get("delta", 0))
    attrs[chave] = attrs[chave] + delta


def ganhar_xp(con: dict[str, Any], _flags: dict[str, Any], attrs: dict[str, Any]) -> None:
    """Acumula XP da rodada em attrs['xp'] (persistido depois como xp_rodada no save)."""

    attrs["xp"] = int(attrs.get("xp", 0)) + int(con.get("valor", 0))


CONSEQUENCE_HANDLERS: dict[str, ConsequenceHandler] = {
    "set_flag": set_flag,
    "alterar_atributo": alterar_atributo,
    "ganhar_xp": ganhar_xp,
}


def aplicar_consequencias(
    consequencias: list[dict[str, Any]], flags: dict[str, Any], attrs: dict[str, Any]
) -> None:
    for con in consequencias:
        tipo = con.get("tipo")
        if tipo not in CONSEQUENCE_HANDLERS:
            raise KeyError(f"Tipo de consequência desconhecido: {tipo}")
        CONSEQUENCE_HANDLERS[tipo](con, flags, attrs)


def clamp_attrs(attrs: dict[str, Any]) -> None:
    for k in ATTRIBUTE_KEYS:
        v = attrs[k]
        attrs[k] = max(0, min(100, v))
