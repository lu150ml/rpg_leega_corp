"""Testes da fórmula de pontuação."""

from __future__ import annotations

import pytest

from app.services import scoring


@pytest.mark.unit
def test_pontuacao_valores_iniciais_save():
    attrs = {
        "energia": 70,
        "reputacao": 50,
        "networking": 50,
        "ansiedade": 0,
        "produtividade": 50,
        "aprendizado": 50,
    }
    # 70 + 100 + 50 + 100 + 100 - 0 = 420
    assert scoring.calcular_pontuacao(attrs) == 420


@pytest.mark.unit
def test_pontuacao_formula_manual():
    attrs = {
        "energia": 10,
        "reputacao": 20,
        "networking": 30,
        "ansiedade": 5,
        "produtividade": 40,
        "aprendizado": 50,
    }
    bruto = 10 + 2 * 20 + 30 + 2 * 40 + 2 * 50 - 3 * 5
    assert scoring.calcular_pontuacao(attrs) == bruto


@pytest.mark.unit
def test_pontuacao_clamp_superior():
    """Clamp em 9999 com bruto acima do teto (valores fora do jogo 0–100, só exemplo)."""
    attrs = {
        "energia": 0,
        "reputacao": 3000,
        "networking": 0,
        "ansiedade": 0,
        "produtividade": 3000,
        "aprendizado": 3000,
    }
    assert scoring.calcular_pontuacao(attrs) == 9999


@pytest.mark.unit
def test_pontuacao_clamp_inferior_com_ansiedade_altissima():
    attrs = {
        "energia": 0,
        "reputacao": 0,
        "networking": 0,
        "ansiedade": 100,
        "produtividade": 0,
        "aprendizado": 0,
    }
    assert scoring.calcular_pontuacao(attrs) == 0
