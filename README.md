# Corporate Survivor

**Corporate Survivor** é um mini RPG corporativo em navegador: você é **trainee** e precisa **sobreviver à primeira semana** na empresa. Atributos (**energia**, **reputação**, **networking**, **ansiedade**, **produtividade**, **aprendizado**) mudam com cada escolha até um de **vários finais** (incluindo fim de semana, demissão por atributo em zero e burnout).

Stack: **`frontend/`** (UI + HTTP) e **`backend/`** (Flask, roteiro em JSON, SQLite). Roteiro em [EVENT_FORMAT.md](docs/EVENT_FORMAT.md); persistência em [SAVE_SYSTEM.md](docs/SAVE_SYSTEM.md) / [API.md](docs/API.md).

---

## Executar (Flask + SQLite)

O roteiro é **orientado a dados** (JSON em `backend/data/events/`). O cliente em `frontend/` exibe estado e envia decisões; regras de jogo, condições e consequências ficam no **backend Flask**.

Regras de produto (atributos persistentes, save automático, continuar/reiniciar, finais múltiplos, eventos condicionais): [docs/GAME_DESIGN.md](docs/GAME_DESIGN.md).

## Requisitos

- **Python 3.10+**
- Navegador recente com suporte a **ES modules** e `fetch`

## Instalação

Clone ou copie o repositório e instale as dependências Python:

```bash
cd backend
pip install -r requirements.txt
```

Opcional: copie `backend/.env.example` para `backend/.env` e ajuste `DATABASE_PATH` ou `FLASK_ENV` se necessário.

## Como rodar

Na pasta `backend`:

```bash
python run.py
```

Abra no navegador: **http://localhost:5000**

O Flask serve os arquivos estáticos em `frontend/` e a API em `/api/...` (mesma origem, sem CORS extra no MVP).

1. Informe um **nome** na tela inicial (cria ou retoma o jogador e o save no SQLite).
2. Leia o evento e escolha uma opção; os atributos atualizam conforme as consequências definidas no JSON.
3. Ao fim do capítulo disponível no roteiro, o servidor calcula o **final** com base nas regras em `backend/app/services/endings.py` e nos textos em `backend/data/endings.json`.

## Estrutura de pastas (resumo)

| Pasta / arquivo | Papel |
|-----------------|--------|
| `frontend/` | HTML, CSS e JavaScript (sem build): apenas UI e chamadas HTTP. |
| `backend/app/` | API Flask, serviços da engine, repositórios SQLite. |
| `backend/data/events/` | Roteiro (`*.json`) + `index.json` com a ordem de leitura. |
| `backend/data/endings.json` | Títulos e descrições dos finais (editável sem alterar lógica numérica). |
| `docs/` | Arquitetura, formato de eventos, API, banco, design. |

## Como adicionar um novo evento

1. Edite ou crie um arquivo em `backend/data/events/` com a lista `eventos` (veja exemplos em `cap01.json`).
2. Registre o arquivo em `backend/data/events/index.json` **na ordem** em que os eventos devem ser considerados.
3. Use `id` estáveis para eventos e opções (o save e o histórico dependem disso).

Documentação detalhada do schema, tipos de **condição** e **consequência**: [`docs/EVENT_FORMAT.md`](docs/EVENT_FORMAT.md).

Para novos tipos de condição ou consequência, registre handlers nos mapas em `backend/app/services/conditions.py` e `consequences.py` (sem espalhar `if/else` por tipo na engine).

## API REST (resumo)

Base URL (dev): `http://localhost:5000`

| Método | Rota | Descrição |
|--------|------|------------|
| `POST` | `/api/players` | Cria ou retorna jogador: body `{"nome":"..."}` |
| `GET` | `/api/players/<nome>` | Dados do jogador |
| `GET` | `/api/saves/<nome>` | Save (atributos, flags, `evento_atual`, `final_obtido`) |
| `PUT` | `/api/saves/<nome>` | Atualização manual do save (uso avançado) |
| `DELETE` | `/api/saves/<nome>` | Reseta progresso (mantém o jogador) |
| `GET` | `/api/events/proximo?nome=<nome>` | Próximo evento elegível e/ou final |
| `GET` | `/api/events/<id>` | Detalhe de um evento |
| `POST` | `/api/decisions` | Body: `nome`, `evento_id`, `opcao_id` — aplica efeitos e devolve save + próximo evento ou final |
| `GET` | `/api/decisions/<nome>` | Histórico de decisões |

Referência completa com exemplos `curl`: [`docs/API.md`](docs/API.md).

## Banco de dados (schema)

SQLite (por padrão `backend/game.db`, configurável via `DATABASE_PATH`): tabelas `players`, `saves`, `decisions`. Esquema e diagrama: [`docs/DATABASE.md`](docs/DATABASE.md).

## Arquitetura

Três camadas: frontend (sem regra de jogo), backend (engine + persistência), dados (JSON + SQLite). Diagramas e dependências: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Finais, atributos e design

- Atributos e faixas: [`docs/PLAYER_ATTRIBUTES.md`](docs/PLAYER_ATTRIBUTES.md)
- Regras dos finais (semana, colapso e ranking): [`docs/ENDINGS.md`](docs/ENDINGS.md)
- Loop do jogo e telas: [`docs/GAME_DESIGN.md`](docs/GAME_DESIGN.md)

## Tecnologias

- Frontend: HTML5, CSS3, JavaScript (módulos ES), sem framework.
- Backend: Python, Flask, sqlite3 (biblioteca padrão).

## Contribuir

Mantenha o roteiro nos JSONs; evite embutir narrativa em código de UI. Novas mecânicas devem preferir tipos declarativos no JSON + handlers registrados no backend, conforme `docs/EVENT_FORMAT.md` e as regras do projeto em `.cursor/rules/`.
