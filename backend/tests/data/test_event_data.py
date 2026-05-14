"""Integridade dos JSONs de roteiro e finais."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services import conditions, consequences, event_service

FINAIS_ESPERADOS_PELO_CODIGO = frozenset(
    {
        "demitido",
        "burnout",
        "risco_operacional",
        "trainee_lenda",
        "promessa_corporativa",
        "sobrevivente_onboarding",
        "funcionario_invisivel",
    }
)


@pytest.mark.data
def test_arquivos_index_existem():
    d = event_service.events_dir()
    index_path = d / "index.json"
    with open(index_path, encoding="utf-8") as f:
        idx = json.load(f)
    arquivos = idx.get("arquivos") or idx.get("files") or []
    for nome in arquivos:
        assert (d / nome).is_file(), f"Faltando {nome}"


@pytest.mark.data
def test_eventos_tem_campos_obrigatorios_e_refs_validas():
    by_id, _ = event_service.catalog()
    for eid, ev in by_id.items():
        assert ev.get("id") == eid
        assert isinstance(ev.get("descricao"), str)
        assert "condicoes" in ev
        assert isinstance(ev["condicoes"], list)
        assert "opcoes" in ev
        assert isinstance(ev["opcoes"], list)
        assert len(ev["opcoes"]) >= 1

        for cond in ev["condicoes"]:
            tipo = cond.get("tipo")
            assert tipo in conditions.CONDITION_HANDLERS, f"Condição inválida: {tipo}"

        for op in ev["opcoes"]:
            assert op.get("id")
            assert isinstance(op.get("texto"), str)
            assert "consequencias" in op
            for con in op["consequencias"]:
                t = con.get("tipo")
                assert t in consequences.CONSEQUENCE_HANDLERS, f"Consequência inválida: {t}"
                if t == "alterar_atributo":
                    assert con.get("chave") in consequences.ATTRIBUTE_KEYS

            prox = op.get("proximo_evento")
            if prox:
                assert prox in by_id, f"proximo_evento {prox!r} inexistente (em {eid})"


@pytest.mark.data
def test_endings_json_alinhado_ao_codigo():
    root = Path(__file__).resolve().parent.parent.parent
    path = root / "data" / "endings.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    finais = data.get("finais", {})
    keys = set(finais.keys())
    assert keys == FINAIS_ESPERADOS_PELO_CODIGO
    for fid, meta in finais.items():
        assert isinstance(meta, dict)
        assert "titulo" in meta and "descricao" in meta
