"""Testes do carregamento de eventos JSON."""

from __future__ import annotations

import pytest

from app.services import event_service


@pytest.mark.unit
def test_catalog_tem_todos_ids_15_eventos():
    by_id, order = event_service.catalog()
    assert len(order) == 15
    assert len(by_id) == 15
    assert set(by_id.keys()) == set(order)


@pytest.mark.unit
def test_ordered_event_ids_respeita_index():
    order = event_service.ordered_event_ids()
    assert order[0] == "CS_D01_E1"
    assert order[-1] == "CS_D05_E3"


@pytest.mark.unit
def test_get_event_existente_e_inexistente():
    ev = event_service.get_event("CS_D01_E1")
    assert ev is not None
    assert ev["id"] == "CS_D01_E1"
    assert event_service.get_event("ID_INEXISTENTE") is None


@pytest.mark.unit
def test_iter_ordered_events_mesma_ordem():
    ordered = event_service.iter_ordered_events()
    ids = [e["id"] for e in ordered]
    assert ids == list(event_service.ordered_event_ids())
