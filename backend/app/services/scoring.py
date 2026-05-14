"""Pontuação final a partir dos atributos (Corporate Survivor)."""

from __future__ import annotations


def calcular_pontuacao(attrs: dict[str, int]) -> int:
    """Pontuação 0–9999: favorece reputação, produtividade e aprendizado; penaliza ansiedade."""

    e = attrs["energia"]
    r = attrs["reputacao"]
    n = attrs["networking"]
    a = attrs["ansiedade"]
    p = attrs["produtividade"]
    ap = attrs["aprendizado"]
    bruto = e + 2 * r + n + 2 * p + 2 * ap - 3 * a
    return max(0, min(9999, bruto))
