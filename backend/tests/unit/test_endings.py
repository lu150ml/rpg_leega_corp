"""Testes de colapso e cadeia de finais."""

from __future__ import annotations

import pytest

from app.services import endings
from app.services.endings import _ATTRS_OPERACIONAIS


@pytest.mark.unit
@pytest.mark.parametrize("chave", list(_ATTRS_OPERACIONAIS))
def test_colapso_demitido_atributo_operacional_zero(chave: str):
    attrs = {
        "energia": 50,
        "reputacao": 50,
        "networking": 50,
        "ansiedade": 30,
        "produtividade": 50,
        "aprendizado": 50,
    }
    attrs[chave] = 0
    assert endings.final_por_colapso_imediato(attrs) == "demitido"
    assert endings.calcular_final_id(attrs) == "demitido"


@pytest.mark.unit
def test_colapso_burnout():
    attrs = {
        "energia": 45,
        "reputacao": 50,
        "networking": 50,
        "ansiedade": 82,
        "produtividade": 50,
        "aprendizado": 50,
    }
    assert endings.final_por_colapso_imediato(attrs) == "burnout"


@pytest.mark.unit
def test_sem_colapso():
    attrs = {
        "energia": 50,
        "reputacao": 50,
        "networking": 50,
        "ansiedade": 30,
        "produtividade": 50,
        "aprendizado": 50,
    }
    assert endings.final_por_colapso_imediato(attrs) is None


@pytest.mark.unit
def test_calcular_risco_operacional():
    attrs = {
        "energia": 50,
        "reputacao": 50,
        "networking": 50,
        "ansiedade": 50,
        "produtividade": 30,
        "aprendizado": 50,
    }
    assert endings.calcular_final_id(attrs) == "risco_operacional"


@pytest.mark.unit
def test_calcular_trainee_lenda():
    attrs = {
        "energia": 45,
        "reputacao": 80,
        "networking": 50,
        "ansiedade": 40,
        "produtividade": 80,
        "aprendizado": 80,
    }
    assert endings.calcular_final_id(attrs) == "trainee_lenda"


@pytest.mark.unit
def test_calcular_promessa_corporativa():
    attrs = {
        "energia": 70,
        "reputacao": 70,
        "networking": 70,
        "ansiedade": 60,
        "produtividade": 70,
        "aprendizado": 70,
    }
    assert endings.calcular_final_id(attrs) == "promessa_corporativa"


@pytest.mark.unit
def test_calcular_sobrevivente_onboarding():
    attrs = {
        "energia": 70,
        "reputacao": 50,
        "networking": 50,
        "ansiedade": 70,
        "produtividade": 50,
        "aprendizado": 50,
    }
    assert endings.calcular_final_id(attrs) == "sobrevivente_onboarding"


@pytest.mark.unit
def test_calcular_funcionario_invisivel():
    attrs = {
        "energia": 50,
        "reputacao": 50,
        "networking": 50,
        "ansiedade": 50,
        "produtividade": 50,
        "aprendizado": 50,
    }
    assert endings.calcular_final_id(attrs) == "funcionario_invisivel"


@pytest.mark.unit
def test_calcular_burnout_via_cadeia_sem_operacional_zero():
    """Burnout antes de risco na função de fim de semana."""
    attrs = {
        "energia": 45,
        "reputacao": 50,
        "networking": 50,
        "ansiedade": 82,
        "produtividade": 50,
        "aprendizado": 50,
    }
    assert endings.calcular_final_id(attrs) == "burnout"
