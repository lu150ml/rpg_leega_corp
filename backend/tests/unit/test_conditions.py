"""Testes de elegibilidade de eventos."""

from __future__ import annotations

import pytest

from app.services import conditions


@pytest.mark.unit
def test_avaliar_condicoes_lista_vazia():
    assert conditions.avaliar_condicoes([], {}, {}) is True


@pytest.mark.unit
def test_flag_ausente():
    conds = [{"tipo": "flag_ausente", "chave": "x"}]
    assert conditions.avaliar_condicoes(conds, {}, {}) is True
    assert conditions.avaliar_condicoes(conds, {"x": False}, {}) is True
    assert conditions.avaliar_condicoes(conds, {"x": True}, {}) is False


@pytest.mark.unit
def test_flag_presente():
    conds = [{"tipo": "flag_presente", "chave": "feito"}]
    assert conditions.avaliar_condicoes(conds, {}, {}) is False
    assert conditions.avaliar_condicoes(conds, {"feito": True}, {}) is True


@pytest.mark.unit
def test_atributo_min_max():
    attrs = {"energia": 42, "ansiedade": 30}
    assert conditions.avaliar_condicoes(
        [{"tipo": "atributo_min", "chave": "energia", "valor": 40}], {}, attrs
    )
    assert not conditions.avaliar_condicoes(
        [{"tipo": "atributo_min", "chave": "energia", "valor": 50}], {}, attrs
    )
    assert conditions.avaliar_condicoes(
        [{"tipo": "atributo_max", "chave": "ansiedade", "valor": 40}], {}, attrs
    )
    assert not conditions.avaliar_condicoes(
        [{"tipo": "atributo_max", "chave": "ansiedade", "valor": 20}], {}, attrs
    )


@pytest.mark.unit
def test_and_em_multiplas_condicoes():
    c = [
        {"tipo": "flag_presente", "chave": "a"},
        {"tipo": "atributo_max", "chave": "ansiedade", "valor": 50},
    ]
    assert conditions.avaliar_condicoes(c, {"a": True}, {"ansiedade": 30})
    assert not conditions.avaliar_condicoes(c, {"a": True}, {"ansiedade": 80})


@pytest.mark.unit
def test_tipo_desconhecido():
    with pytest.raises(KeyError, match="desconhecido"):
        conditions.avaliar_condicoes([{"tipo": "condicao_magica"}], {}, {})
