# Atributos do jogador (Corporate Survivor)

Seis dimensões, em geral na faixa **0–100** (valores são limitados pelo engine ao aplicar consequências). Valores iniciais típicos no save:

| Chave API / JSON | Nome na UI | Inicial | Significado |
|------------------|------------|---------|-------------|
| `energia` | Energia | **70** | Disposição física e mental para aguentar a semana; **muito baixa** aumenta risco de desligamento (final **Risco operacional**). |
| `reputacao` | Reputação | **50** | Como gestores e pares te enxergam. |
| `networking` | Networking | **50** | Relação e visibilidade no time. |
| `ansiedade` | Ansiedade | **0** | Nível de tensão (quanto **maior**, **pior**); pivotal para **Sobrevivente** e **Risco operacional**. |
| `produtividade` | Produtividade | **50** | Entrega e foco nas tarefas. |
| `aprendizado` | Aprendizado | **50** | Quanto você absorve processos e conteúdo novo na empresa. |

As regras numéricas dos **finais** (incluindo colapso imediato e fim de semana) estão em [ENDINGS.md](./ENDINGS.md) e em `backend/app/services/endings.py`.
