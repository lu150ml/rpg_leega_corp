# Banco de dados (SQLite)

Arquivo padrão: `backend/game.db`. Caminho configurável por `DATABASE_PATH` (vide `backend/.env.example`).

Schema idempotente: `backend/app/db/schema.sql`.

## Diagrama ER

```mermaid
erDiagram
    PLAYERS ||--o| SAVES : possui
    PLAYERS ||--o{ DECISIONS : registra

    PLAYERS {
        INTEGER id PK
        TEXT nome UK
        TEXT criado_em
    }

    SAVES {
        INTEGER player_id PK FK
        TEXT evento_atual
        INTEGER energia
        INTEGER reputacao
        INTEGER networking
        INTEGER ansiedade
        INTEGER produtividade
        INTEGER aprendizado
        TEXT flags_json
        TEXT final_obtido
        TEXT atualizado_em
    }

    DECISIONS {
        INTEGER id PK
        INTEGER player_id FK
        TEXT evento_id
        TEXT opcao_id
        TEXT decidido_em
    }
```

## Tabelas

### `players`

- `nome` único (identifica o save por nome digitado).

### `saves`

- Um save por jogador (`player_id` PK).
- `flags_json` — objeto JSON serializado em texto (mapa chave → valor).
- `final_obtido` — string do id de final ou `NULL` se ainda não terminou.

### `decisions`

- Histórico append-only por decisão do jogador (útil para debug e analytics futuro).

## Migrações

Na subida da app, após `schema.sql`, roda `migrations.apply_saves_corporate_survivor_attrs`: se existir tabela `saves` **antiga** (sem coluna `energia`), os dados são recopiados para o modelo **Corporate Survivor** (`energia`, `ansiedade`, `aprendizado`, etc.). Bancos já no formato novo são ignorados.

Para evoluções adicionais, pode-se estender `backend/app/db/migrations.py` ou adotar numeração (`001_*.sql`) e tabela `schema_version`.

## Boas práticas

- Habilitar `PRAGMA foreign_keys = ON` por conexão.
- Não expor SQL à camada HTTP — usar `repositories.py`.
