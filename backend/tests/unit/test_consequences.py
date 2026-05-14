"""Testes de consequências e clamp de atributos."""

from __future__ import annotations

import pytest

from app.services import consequences


@pytest.mark.unit
def test_set_flag():
    flags: dict = {}
    attrs = {k: 50 for k in consequences.ATTRIBUTE_KEYS}
    consequences.aplicar_consequencias(
        [{"tipo": "set_flag", "chave": "ok", "valor": True}], flags, attrs
    )
    assert flags["ok"] is True


@pytest.mark.unit
def test_alterar_atributo_ignora_chave_invalida():
    flags: dict = {}
    attrs = {k: 50 for k in consequences.ATTRIBUTE_KEYS}
    consequences.aplicar_consequencias(
        [{"tipo": "alterar_atributo", "chave": "hp", "delta": 99}], flags, attrs
    )
    assert attrs["energia"] == 50


@pytest.mark.unit
def test_alterar_atributo_soma():
    flags: dict = {}
    attrs = {k: 50 for k in consequences.ATTRIBUTE_KEYS}
    consequences.aplicar_consequencias(
        [
            {"tipo": "alterar_atributo", "chave": "energia", "delta": 10},
            {"tipo": "alterar_atributo", "chave": "ansiedade", "delta": -5},
        ],
        flags,
        attrs,
    )
    assert attrs["energia"] == 60
    assert attrs["ansiedade"] == 45


@pytest.mark.unit
def test_clamp_attrs():
    attrs = {k: 50 for k in consequences.ATTRIBUTE_KEYS}
    attrs["energia"] = 120
    attrs["ansiedade"] = -10
    consequences.clamp_attrs(attrs)
    assert attrs["energia"] == 100
    assert attrs["ansiedade"] == 0


@pytest.mark.unit
def test_tipo_desconhecido():
    with pytest.raises(KeyError, match="desconhecido"):
        consequences.aplicar_consequencias([{"tipo": "explodir"}], {}, {})
