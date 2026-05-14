"""Cálculo de final pelo perfil de atributos e textos em data/endings.json."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
_ENDINGS_PATH = _BACKEND_ROOT / "data" / "endings.json"

_ATTRS_OPERACIONAIS = (
    "energia",
    "reputacao",
    "networking",
    "produtividade",
    "aprendizado",
)


def algum_atributo_operacional_zero(attrs: dict[str, int]) -> bool:
    """Ansiedade em 0 é desejável; os demais em 0 ensejam desligamento imediato."""

    return any(int(attrs[k]) <= 0 for k in _ATTRS_OPERACIONAIS)


def final_por_colapso_imediato(
    attrs: dict[str, int], flags: dict[str, Any] | None = None
) -> str | None:
    """Finais que encerram a partida antes da sexta-feira (sem próximo evento na cadeia)."""

    flags = flags or {}
    if flags.get("pediu_as_contas"):
        return "pediu_as_contas"

    if algum_atributo_operacional_zero(attrs):
        return "demitido"
    anx = attrs["ansiedade"]
    en = attrs["energia"]
    # Burnout: tensão alta + energia destruída (sem necessariamente stats operacionais em zero).
    if anx >= 82 and en <= 45:
        return "burnout"
    return None


def calcular_final_id(
    attrs: dict[str, int], flags: dict[str, Any] | None = None
) -> str:
    """Retorna o identificador do primeiro final cuja regra casa (ordem exclusiva)."""

    flags = flags or {}
    if flags.get("pediu_as_contas"):
        return "pediu_as_contas"

    if algum_atributo_operacional_zero(attrs):
        return "demitido"

    prod = attrs["produtividade"]
    rep = attrs["reputacao"]
    ap = attrs["aprendizado"]
    net = attrs["networking"]
    anx = attrs["ansiedade"]
    en = attrs["energia"]

    if anx >= 82 and en <= 45:
        return "burnout"

    if prod <= 30 or rep <= 30 or ap <= 30 or anx >= 85 or en <= 20:
        return "risco_operacional"
    if prod >= 80 and rep >= 80 and ap >= 80 and anx <= 40 and en >= 45:
        return "trainee_lenda"
    media = (prod + rep + net + ap) / 4.0
    if media >= 70 and anx <= 60:
        return "promessa_corporativa"
    if anx >= 70:
        return "sobrevivente_onboarding"
    return "funcionario_invisivel"


@lru_cache(maxsize=1)
def _endings_payload() -> dict[str, Any]:
    with open(_ENDINGS_PATH, encoding="utf-8") as f:
        return json.load(f)


def final_para_resposta(final_id: str) -> dict[str, Any]:
    """Monta dict com id, titulo e descricao vindos do JSON."""

    finais: dict[str, Any] = _endings_payload().get("finais", {})
    meta = finais.get(final_id, {})
    return {
        "id": final_id,
        "titulo": meta.get("titulo", final_id),
        "descricao": meta.get("descricao", ""),
    }
