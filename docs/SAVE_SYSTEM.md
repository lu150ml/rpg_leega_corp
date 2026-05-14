# Persistência (save)

O save **localStorage** do antigo `index.html` na raiz foi **removido**. A partida é persistida no **SQLite** via API:

- `GET/PUT/DELETE /api/saves/<nome>` — veja [API.md](./API.md)
- Esquema: [DATABASE.md](./DATABASE.md)
