# Game design

## Regras obrigatórias (produto)

- **Atributos persistentes**: energia, reputação, networking, ansiedade, produtividade e aprendizado são gravados no SQLite a cada decisão e retornam com o mesmo nome de jogador.
- **Impacto real das escolhas**: consequências (`alterar_atributo`, `set_flag`) alteram o save; finais dependem do perfil acumulado.
- **Eventos condicionais**: novos passos do roteiro podem exigir flags ou patamares de atributo (`condicoes` no JSON); o servidor ignora eventos inelegíveis e pode **reparar** o ponteiro `evento_atual` quando o estado deixa de casar (ex.: cena opcional por reputação).
- **Save automático**: toda escolha confirmada dispara `POST /api/decisions`, que persiste save e histórico — não é necessário salvar manualmente.
- **Continuar partida**: usar o **mesmo nome** na tela inicial recarrega o último estado do banco.
- **Reiniciar jornada**: **Reiniciar jornada** (durante o jogo ou na tela de final) chama `DELETE /api/saves/<nome>` e volta ao primeiro evento elegível.
- **Múltiplos finais**: vários desfechos distintos (semana, colapso e perfil), calculados em `backend/app/services/endings.py` e descritos em [ENDINGS.md](./ENDINGS.md).

## Pilares

- **Corporate Survivor**: mini RPG corporativo — o jogador é **trainee** e precisa **sobreviver à primeira semana** na empresa.
- **Fantasia de escritório**: microdecisões credíveis (energia, prazo, relacionamento, ansiedade).
- **Consequência transparente**: atributos sobem/descem; o jogador sente o “preço” das escolhas.
- **Replay curto**: sessões de alguns minutos; finais distintos incentivam nova partida com outro nome (save por nome).

## Atributos (resumo)

Seis dimensões (ver [PLAYER_ATTRIBUTES.md](./PLAYER_ATTRIBUTES.md)): **energia**, **reputação**, **networking**, **ansiedade**, **produtividade**, **aprendizado**. Ansiedade alta e energia baixa puxam para finais mais duros.

## Telas

1. **Login (nome)** — cria ou retoma jogador; carrega save do SQLite.
2. **Evento** — descrição, personagem/fundo opcionais, opções clicáveis.
3. **HUD** — barras de atributos atualizadas após cada decisão (via resposta da API).
4. **Final** — título e descrição do ending calculado no servidor.

## Loop principal

1. Jogador vê o evento atual (`GET /api/events/proximo` ou estado do save).
2. Escolhe uma opção.
3. `POST /api/decisions` aplica consequências e devolve novo estado.
4. Se houver `proximo_evento`, o fluxo continua; senão, o servidor calcula o **final** e o cliente mostra a tela de encerramento.

## Finais

Regras numéricas em [ENDINGS.md](./ENDINGS.md). O servidor avalia na ordem de prioridade documentada; o primeiro critério satisfeito define o final.

## Conteúdo

O roteiro principal fica em `backend/data/events/` (ex.: `semana_corporate.json`). Novos capítulos seguem [EVENT_FORMAT.md](./EVENT_FORMAT.md).
