"""Fixtures compartilhadas — app Flask com SQLite em arquivo temporário."""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Garante imports a partir da pasta backend/
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

# Acumulador para relatório TXT (uma entrada por teste na fase "call")
_relatorio_linhas: list[dict[str, str | float]] = []

_RELATORIO_PATH = _BACKEND_ROOT / "relatorio_testes.txt"


def pytest_sessionstart(session: pytest.Session) -> None:
    _relatorio_linhas.clear()


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when != "call":
        return

    if report.passed:
        status = "PASSOU"
    elif report.failed:
        status = "FALHOU"
    elif report.skipped:
        status = "PULADO"
    else:
        status = "ERRO"

    msg = ""
    if report.failed or report.skipped:
        msg = getattr(report, "longreprtext", None) or str(report.longrepr or "")

    _relatorio_linhas.append(
        {
            "nodeid": report.nodeid,
            "status": status,
            "duracao": float(report.duration or 0.0),
            "mensagem": msg.strip(),
        }
    )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    passou = sum(1 for r in _relatorio_linhas if r["status"] == "PASSOU")
    falhou = sum(1 for r in _relatorio_linhas if r["status"] == "FALHOU")
    pulado = sum(1 for r in _relatorio_linhas if r["status"] == "PULADO")
    erro = sum(1 for r in _relatorio_linhas if r["status"] == "ERRO")
    total = len(_relatorio_linhas)

    linhas_txt: list[str] = [
        "=" * 52,
        " RELATÓRIO DE TESTES — Corporate Survivor",
        f" Data/hora: {agora}",
        f" Exit status pytest: {exitstatus}",
        "=" * 52,
        "",
    ]

    for r in _relatorio_linhas:
        d = float(r["duracao"])
        nome = str(r["nodeid"])
        stat = str(r["status"])
        linhas_txt.append(f"{stat:<7} | {nome} ({d:.3f}s)")

    falhas_msgs = [r for r in _relatorio_linhas if r["status"] != "PASSOU"]

    linhas_txt.extend(
        [
            "",
            "-" * 52,
            "FALHAS / ERROS / PULADOS (detalhe):",
            "-" * 52,
        ]
    )

    if not falhas_msgs:
        linhas_txt.append("(nenhum)")
    else:
        for r in falhas_msgs:
            linhas_txt.append(f"[{r['nodeid']}]")
            m = str(r["mensagem"]).strip()
            if m:
                for part in m.splitlines():
                    linhas_txt.append(f"  {part}")
            linhas_txt.append("")

    linhas_txt.extend(
        [
            "=" * 52,
            f" RESUMO: {passou} passaram | {falhou} falharam | {pulado} pulados"
            f" | {erro} erros | total {total}",
            "=" * 52,
        ]
    )

    _RELATORIO_PATH.write_text("\n".join(linhas_txt) + "\n", encoding="utf-8")


def make_player(client, nome: str = "JogadorTeste"):
    """POST /api/players; retorna o JSON do jogador."""
    resp = client.post("/api/players", json={"nome": nome})
    assert resp.status_code in (200, 201), resp.get_data(as_text=True)
    return resp.get_json()


@pytest.fixture
def app(tmp_path, monkeypatch):
    """
    App com banco em arquivo temporário (não usar :memory: — init_db fecha a
    conexão inicial e perderia o schema com SQLite in-memory clássico).
    """
    db_path = tmp_path / "test_game.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))

    # Import após monkeypatch para create_app() ler o env correto
    from app import create_app  # pylint: disable=import-outside-toplevel

    application = create_app()
    application.config.update({"TESTING": True})
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_conn(app):
    """Conexão SQLite direta ao mesmo arquivo usado pela app."""
    conn = sqlite3.connect(app.config["DATABASE_PATH"])
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()
