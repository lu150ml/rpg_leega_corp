# API REST

Base URL (desenvolvimento): `http://localhost:5000`

Todas as respostas relevantes são `Content-Type: application/json`. Erros comuns: `400` (payload inválido), `404` (recurso inexistente), `500` (erro interno).

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/players` | Cria jogador ou retorna existente pelo nome |
| `GET` | `/api/players/<nome>` | Dados do jogador |
| `GET` | `/api/saves/<nome>` | Save (atributos, flags, evento atual, final) |
| `PUT` | `/api/saves/<nome>` | Atualiza save manualmente (uso avançado / debug) |
| `DELETE` | `/api/saves/<nome>` | Remove save (reseta progresso mantendo jogador) |
| `GET` | `/api/events/proximo?nome=<nome>` | Próximo evento elegível |
| `GET` | `/api/events/<id>` | Detalhe de um evento por id |
| `POST` | `/api/decisions` | Registra decisão e aplica consequências |
| `GET` | `/api/decisions/<nome>` | Histórico de decisões |

---

### `POST /api/players`

**Body:**

```json
{ "nome": "Alex" }
```

**201 / 200** — exemplo:

```json
{ "id": 1, "nome": "Alex", "criado_em": "..." }
```

**curl:**

```bash
curl -s -X POST http://localhost:5000/api/players -H "Content-Type: application/json" -d "{\"nome\":\"Alex\"}"
```

---

### `GET /api/players/<nome>`

**200:**

```json
{ "id": 1, "nome": "Alex", "criado_em": "..." }
```

**curl:**

```bash
curl -s http://localhost:5000/api/players/Alex
```

---

### `GET /api/saves/<nome>`

**200:**

```json
{
  "player_id": 1,
  "evento_atual": "CS_D01_E2",
  "energia": 68,
  "reputacao": 55,
  "networking": 54,
  "ansiedade": 7,
  "produtividade": 50,
  "aprendizado": 50,
  "dia_atual": 1,
  "eventos_hoje": 1,
  "flags": { "ok_CS_D01_E1": true, "trainee_primeiro_dia": true },
  "final_obtido": null,
  "atualizado_em": "..."
}
```

**curl:**

```bash
curl -s http://localhost:5000/api/saves/Alex
```

---

### `PUT /api/saves/<nome>`

**Body** (campos opcionais): `evento_atual`, `energia`, `reputacao`, `networking`, `ansiedade`, `produtividade`, `aprendizado`, `dia_atual`, `eventos_hoje`, `flags`, `final_obtido`.

**curl:**

```bash
curl -s -X PUT http://localhost:5000/api/saves/Alex -H "Content-Type: application/json" -d "{\"ansiedade\":10}"
```

---

### `DELETE /api/saves/<nome>`

**204** sem corpo.

**curl:**

```bash
curl -s -o NUL -w "%{http_code}" -X DELETE http://localhost:5000/api/saves/Alex
```

---

### `GET /api/events/proximo?nome=<nome>`

**200** — evento completo + metadado `id` ou `null` se não houver evento:

```json
{ "evento": { "id": "CS_D01_E1", "descricao": "...", "opcoes": [] } }
```

**curl:**

```bash
curl -s "http://localhost:5000/api/events/proximo?nome=Alex"
```

---

### `GET /api/events/<id>`

**200:** objeto evento.

**curl:**

```bash
curl -s http://localhost:5000/api/events/CS_D01_E1
```

---

### `POST /api/decisions`

**Body:**

```json
{
  "nome": "Alex",
  "evento_id": "CS_D01_E1",
  "opcao_id": "opt_ok_CS_D01_E1_a"
}
```

**200** — exemplo com próximo evento:

```json
{
  "save": { "...": "..." },
  "proximo_evento": { "id": "CS_D01_E2", "...": "..." },
  "final": null
}
```

Exemplo encerrando narrativa:

```json
{
  "save": { "final_obtido": "promessa_corporativa", "...": "..." },
  "proximo_evento": null,
  "final": { "id": "promessa_corporativa", "titulo": "...", "descricao": "..." }
}
```

**curl:**

```bash
curl -s -X POST http://localhost:5000/api/decisions -H "Content-Type: application/json" -d "{\"nome\":\"Alex\",\"evento_id\":\"CS_D01_E1\",\"opcao_id\":\"opt_ok_CS_D01_E1_a\"}"
```

---

### `GET /api/decisions/<nome>`

**200:**

```json
{
  "decisoes": [
    { "evento_id": "CS_D01_E1", "opcao_id": "opt_ok_CS_D01_E1_a", "decidido_em": "..." }
  ]
}
```

**curl:**

```bash
curl -s http://localhost:5000/api/decisions/Alex
```
