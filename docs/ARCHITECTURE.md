# Arquitetura

O sistema segue **três camadas** com dependência **unidirecional**: o frontend só conversa com HTTP; rotas só validam e delegam; serviços contêm regra de jogo e leitura de roteiro; repositórios isolam SQLite.

## Diagrama (camadas)

```mermaid
flowchart TB
    subgraph frontend [Frontend — HTML/CSS/JS]
        ui[components/*]
        store[state/store.js]
        client[api/client.js]
    end
    subgraph backend [Backend — Flask]
        routes[routes/*]
        engine[services/game_engine.py]
        endings[services/endings.py]
        repos[db/repositories.py]
    end
    subgraph dados [Dados]
        json[data/events/*.json]
        sqlite[(SQLite game.db)]
    end

    ui --> store
    store --> client
    client -->|HTTP JSON| routes
    routes --> engine
    engine --> endings
    engine --> repos
    repos <--> sqlite
    engine --> json
```

## Regras de dependência

| Origem | Destino permitido |
|--------|-------------------|
| `frontend/` | Apenas API HTTP via `api/client.js` |
| `backend/app/routes/` | Serviços + repositórios (sem SQL direto) |
| `backend/app/services/` | Repositórios, JSON de eventos, `endings.json` — sem DOM |
| `backend/app/db/repositories.py` | SQLite, schema conhecido |

- **Roteiro** não vive em código Python/JavaScript de produção — apenas em `backend/data/events/*.json`.

## Fluxo de uma decisão

```mermaid
sequenceDiagram
    participant UI as Frontend
    participant API as POST /api/decisions
    participant GE as game_engine
    participant DB as repositories

    UI->>API: nome, evento_id, opcao_id
    API->>GE: aplicar_decisao
    GE->>DB: carregar save + jogador
    GE->>GE: validar opcao e consequencias
    GE->>DB: persistir atributos, flags, evento_atual
    alt proximo_evento ausente
        GE->>GE: endings.calcular
        GE->>DB: gravar final_obtido
    end
    GE-->>API: estado + proximo ou final
    API-->>UI: JSON
```

## Pastas principais

- `frontend/` — SPA leve por módulos ES (cliente da API).
- `backend/app/` — factory Flask, blueprints, serviços, DB.
- `backend/data/events/` — índice e capítulos JSON.
- `docs/` — contratos e guias (este arquivo, API, formato de evento, etc.).
