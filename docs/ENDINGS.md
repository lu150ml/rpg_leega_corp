# Finais

Os finais são calculados **no servidor** quando:

1. **Colapso imediato** — após uma decisão (ou ao sincronizar com `GET /api/events/proximo`), se algum atributo operacional chega a **0** ou se o par **ansiedade / energia** indica **burnout**, a partida encerra **antes** do fim linear da semana.
2. **Fim de semana** — na última escolha da cadeia, quando **não** há `proximo_evento`, o jogo encerra na **sexta-feira** e o final é escolhido pela ordem abaixo (sem colapso já tratado).

Textos em `backend/data/endings.json`. Lógica: `backend/app/services/endings.py`.

## Colapso imediato (prioridade absoluta)

| Condição | ID | Nome |
|----------|-----|------|
| `energia`, `reputacao`, `networking`, `produtividade` ou `aprendizado` ≤ **0** | `demitido` | Demitido no Período de Experiência |
| `ansiedade` ≥ **82** e `energia` ≤ **45** | `burnout` | Burnout em Tempo Recorde |

*(Ansiedade em 0 é favorável; não desencadeia demissão.)*

## Finais ao terminar a semana (sem colapso)

Ordem **exclusiva**: o **primeiro** critério satisfeito vence.

| Ordem | ID | Nome | Regra (resumo) |
|-------|-----|------|----------------|
| 1 | `risco_operacional` | Risco operacional | Produtividade, reputação ou aprendizado ≤ **30**, **ou** ansiedade ≥ **85**, **ou** energia ≤ **20** |
| 2 | `trainee_lenda` | Destaque da equipe | Produtividade, reputação e aprendizado ≥ **80**, ansiedade ≤ **40** e energia ≥ **45** |
| 3 | `promessa_corporativa` | Promessa corporativa | Média de produtividade, reputação, networking e aprendizado ≥ **70** **e** ansiedade ≤ **60** |
| 4 | `sobrevivente_onboarding` | Sobrevivente do onboarding | Ansiedade ≥ **70** |
| 5 | `funcionario_invisivel` | Sobrevivência normal | Caso padrão |

## Observações

- **Média** em `promessa_corporativa` usa quatro atributos (não inclui ansiedade nem energia).
- **“Demitido no Período de Experiência”** corresponde ao piso **0** em qualquer atributo operacional listado no colapso.
- **“Sobrevivência normal”** é o desfecho padrão ao concluir a semana sem encaixar nos critérios acima.
