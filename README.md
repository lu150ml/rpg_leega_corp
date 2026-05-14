# Corporate Survivor

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-API-000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

> **Sobreviva à primeira semana como trainee.** Escolhas alteram atributos, flags e o desfecho — regra de jogo no servidor; a interface só exibe o estado e envia decisões.

---

## Sobre o jogo

- **Protagonista:** trainee no primeiro dia de trabalho.
- **Duração:** 5 dias úteis, **3 eventos principais** por dia (`backend/data/events/semana_corporate.json`).
- **Persistência:** SQLite — mesmo **nome** retoma a partida; é possível **reiniciar** a jornada (API).

**Atributos** (0–100, `snake_case` na API):

| Atributo       | Papel resumido              |
|----------------|-----------------------------|
| `energia`      | Disposição para aguentar    |
| `reputacao`    | Imagem com gestores e pares |
| `networking`   | Visibilidade no time        |
| `ansiedade`    | Tensão (quanto maior, pior) |
| `produtividade`| Entrega e foco              |
| `aprendizado`  | Capacidade de absorção      |

Detalhes: [`docs/PLAYER_ATTRIBUTES.md`](docs/PLAYER_ATTRIBUTES.md).

---

## Como rodar

### Requisitos

- **Python 3.10+**
- Navegador com **ES modules** e `fetch`

### Instalação

```bash
cd backend
pip install -r requirements.txt
```

Opcional: copie `backend/.env.example` para `backend/.env` e ajuste `DATABASE_PATH` se quiser outro caminho para o SQLite.

### Subir o servidor

```bash
cd backend
python run.py
```

Abra **http://localhost:5000** — o Flask serve o `frontend/` e a API em **`/api/...`** (mesma origem, sem CORS extra no MVP).

---

## Estrutura do projeto

| Caminho | Função |
|---------|--------|
| [`frontend/`](frontend/) | HTML, CSS, JS modular — só UI e chamadas HTTP |
| [`backend/app/`](backend/app/) | Flask: rotas, engine, serviços, repositórios |
| [`backend/data/events/`](backend/data/events/) | Roteiro JSON + [`index.json`](backend/data/events/index.json) (ordem de leitura) |
| [`backend/data/endings.json`](backend/data/endings.json) | Textos dos finais (IDs fixos na lógica em `endings.py`) |
| [`docs/`](docs/) | Arquitetura, API, formato de eventos, banco, design |

Convenções do projeto: regras em [`.cursor/rules/`](.cursor/rules/) (roteiro só em JSON, sem regra de jogo no frontend).

---

## Como jogar

1. **Tela inicial** — cadastre um **nome** (cria ou retoma jogador + save).
2. **Cada evento** — leia o cenário e escolha **uma** das opções; o servidor aplica consequências e grava o progresso.
3. **Fim** — ao terminar a semana (ou em **colapso** por atributos), o servidor calcula o **final**, a **pontuação** e registra o **ranking global**.

Fluxo e telas: [`docs/GAME_DESIGN.md`](docs/GAME_DESIGN.md).

---

## Finais disponíveis

Resumo — ordem e regras completas: [`docs/ENDINGS.md`](docs/ENDINGS.md).

**Colapso (pode encerrar antes da sexta):**

| Final | Gatilho (resumo) |
|-------|-------------------|
| Demitido no Período de Experiência | `energia`, `reputacao`, `networking`, `produtividade` ou `aprendizado` ≤ 0 |
| Burnout em Tempo Recorde | `ansiedade` ≥ 82 e `energia` ≤ 45 |

**Fim de semana (última escolha da cadeia):** entre outros, **Risco operacional**, **Destaque da equipe**, **Promessa corporativa**, **Sobrevivente do onboarding**, **Sobrevivência normal** — conforme perfil após a última decisão.

---

## API (referência rápida)

**Base (dev):** `http://localhost:5000`

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/players` | Cria ou retorna jogador (`{"nome": "..."}`) |
| `GET` | `/api/players/<nome>` | Dados do jogador |
| `GET` | `/api/saves/<nome>` | Save (atributos, flags, dia, `evento_atual`, `final_obtido`, …) |
| `PUT` | `/api/saves/<nome>` | Atualização manual (debug / avançado) |
| `DELETE` | `/api/saves/<nome>` | Zera progresso (mantém o jogador) |
| `GET` | `/api/events/proximo?nome=<nome>` | Próximo evento elegível e/ou tela de final |
| `GET` | `/api/events/<id>` | Detalhe de um evento |
| `POST` | `/api/decisions` | `nome`, `evento_id`, `opcao_id` — aplica efeitos |
| `GET` | `/api/decisions/<nome>` | Histórico de decisões |
| `GET` | `/api/ranking?limite=20` | Ranking global (scores de partidas encerradas) |

Exemplos `curl` e payloads: [`docs/API.md`](docs/API.md).  
Esquema SQLite: [`docs/DATABASE.md`](docs/DATABASE.md).

---

## Documentação

| Doc | Conteúdo |
|-----|----------|
| [`docs/TECHNICAL_REFERENCE.md`](docs/TECHNICAL_REFERENCE.md) | Referência única: arquitetura, API, banco, engine, parâmetros e JSON |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Camadas e fluxo de decisão |
| [`docs/EVENT_FORMAT.md`](docs/EVENT_FORMAT.md) | Schema de eventos, condições e consequências |
| [`docs/API.md`](docs/API.md) | Referência REST |
| [`docs/DATABASE.md`](docs/DATABASE.md) | Tabelas e migrações |
| [`docs/GAME_DESIGN.md`](docs/GAME_DESIGN.md) | Regras de produto e loop |
| [`docs/ENDINGS.md`](docs/ENDINGS.md) | Finais e prioridades |
| [`docs/PLAYER_ATTRIBUTES.md`](docs/PLAYER_ATTRIBUTES.md) | Atributos |

---

## Tecnologias

- **Frontend:** HTML5, CSS3, JavaScript (módulos ES), sem build e sem framework.
- **Backend:** Python, Flask, SQLite (`sqlite3` da biblioteca padrão).

---

## Contribuir

Mantenha **narrativa e regras declarativas** em `backend/data/events/*.json`. Evite embutir roteiro ou cálculo de jogo no frontend. Novas mecânicas: preferir tipos no JSON + handlers em [`backend/app/services/conditions.py`](backend/app/services/conditions.py) e [`consequences.py`](backend/app/services/consequences.py).
