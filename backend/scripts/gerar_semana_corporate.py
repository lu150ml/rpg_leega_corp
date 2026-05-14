"""Gera backend/data/events/semana_corporate.json (15 eventos principais, 5 dias x 3)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "events" / "semana_corporate.json"

NARRATIVAS = [
    ("Dia 1 —", "Chegada", "O RH te apresenta a área. Seu crachá ainda parece estranho no bolso.", None),
    ("Dia 1 —", "Mesa", "Sua mesa está entre dois analistas experientes. O chefe passa e cumprimenta a equipe.", "chefe"),
    ("Dia 1 —", "Fim do dia", "O escritório esvazia. Você repassa mentalmente tudo que ouviu.", None),
    ("Dia 2 —", "E-mail", "Caixa de entrada cheia. Três pedidos urgentes com prazos sobrepostos.", "chefe"),
    ("Dia 2 —", "Stand-up", "A reunião diária: todos falam em 30 segundos o que farão.", "colega"),
    ("Dia 2 —", "Tarde", "Um cliente interno cobra status de uma entrega que ainda não existe.", "cliente_interno"),
    ("Dia 3 —", "Planilha", "Você herdou uma planilha com fórmulas quebradas e notas manuscritas na margem.", None),
    ("Dia 3 —", "Almoço", "Um colega convida você para almoçar com o pessoal mais sênior.", "colega"),
    ("Dia 3 —", "Feedback", "O líder pede cinco minutos para uma conversa rápida sobre expectativas.", "lider"),
    ("Dia 4 —", "Crise leve", "Um número na apresentação não bate. O time olha para a sala.", "chefe"),
    ("Dia 4 —", "Pair", "Você programa ou revisa o trabalho lado a lado com outra pessoa.", "colega"),
    ("Dia 4 —", "E-mail tardio", "Às 18h chega um e-mail com 'URGENTE' no assunto.", None),
    ("Dia 5 —", "Revisão", "Última revisão antes de subir o pacote para o cliente.", "lider"),
    ("Dia 5 —", "Apresentação", "Você tem um slide para apoiar o time na chamada.", "chefe"),
    ("Dia 5 —", "Encerramento", "A semana acaba. O gerente junta todo mundo para um fechamento simbólico.", "gerente"),
]


def opt_completa(ok_key: str, next_id: str | None, extra_cons: list) -> list[dict]:
    cons = [{"tipo": "set_flag", "chave": ok_key, "valor": True}, *extra_cons]
    o: dict = {
        "id": f"opt_{ok_key}_a",
        "texto": "Responder com postura proativa e clara.",
        "consequencias": [
            *cons,
            {"tipo": "alterar_atributo", "chave": "reputacao", "delta": 6},
            {"tipo": "alterar_atributo", "chave": "produtividade", "delta": 5},
            {"tipo": "alterar_atributo", "chave": "ansiedade", "delta": 4},
            {"tipo": "alterar_atributo", "chave": "energia", "delta": -4},
        ],
    }
    if next_id:
        o["proximo_evento"] = next_id
    o2: dict = {
        "id": f"opt_{ok_key}_b",
        "texto": "Priorizar precisão, pedir tempo ou alinhar antes de agir.",
        "consequencias": [
            *cons,
            {"tipo": "alterar_atributo", "chave": "aprendizado", "delta": 8},
            {"tipo": "alterar_atributo", "chave": "ansiedade", "delta": -3},
            {"tipo": "alterar_atributo", "chave": "networking", "delta": 4},
            {"tipo": "alterar_atributo", "chave": "energia", "delta": 2},
        ],
    }
    if next_id:
        o2["proximo_evento"] = next_id
    return [o, o2]


def main() -> None:
    eventos: list[dict] = []
    for i, (dia_lbl, titulo, desc, pers) in enumerate(NARRATIVAS):
        d = i // 3 + 1
        m = i % 3 + 1
        eid = f"CS_D0{d}_E{m}"
        ok_key = f"ok_{eid}"
        prev_ok = f"ok_CS_D0{(i - 1) // 3 + 1}_E{(i - 1) % 3 + 1}" if i > 0 else None

        if i == 0:
            condicoes = [{"tipo": "flag_ausente", "chave": ok_key}]
        else:
            assert prev_ok is not None
            condicoes = [
                {"tipo": "flag_presente", "chave": prev_ok},
                {"tipo": "flag_ausente", "chave": ok_key},
            ]

        texto = f"{dia_lbl} {titulo}. {desc}"
        next_id = None
        if i < len(NARRATIVAS) - 1:
            nd = (i + 1) // 3 + 1
            nm = (i + 1) % 3 + 1
            next_id = f"CS_D0{nd}_E{nm}"

        extra: list = []
        if i == 0:
            extra = [{"tipo": "set_flag", "chave": "trainee_primeiro_dia", "valor": True}]

        opcoes = opt_completa(ok_key, next_id, extra)

        eventos.append(
            {
                "id": eid,
                "dia": d,
                "momento_no_dia": m,
                "evento_principal": True,
                "descricao": texto,
                "fundo": "escritorio",
                "personagem": pers,
                "condicoes": condicoes,
                "opcoes": opcoes,
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"eventos": eventos}, f, ensure_ascii=False, indent=2)
    print("gravado", OUT, "eventos", len(eventos))


if __name__ == "__main__":
    main()
