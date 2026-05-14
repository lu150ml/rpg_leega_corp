# Formato de eventos (JSON)

Eventos descrevem uma cena interativa: texto, condições de elegibilidade e opções com efeitos.

## Estrutura de arquivo

Cada arquivo listado em `backend/data/events/index.json` deve ter uma chave **`eventos`**: array de objetos evento.

## Objeto evento

| Campo | Obrigatório | Tipo | Descrição |
|-------|-------------|------|-----------|
| `id` | sim | string | Identificador estável, ex. `cap01_primeiro_dia` |
| `descricao` | sim | string | Texto mostrado ao jogador |
| `condicoes` | sim | array | Lista de condições (pode ser `[]`) |
| `opcoes` | sim | array | Escolhas disponíveis |
| `fundo` | não | string | Chave lógica de arte de fundo |
| `personagem` | não | string | Chave lógica de retrato |

## Objeto opção

| Campo | Obrigatório | Tipo | Descrição |
|-------|-------------|------|-----------|
| `id` | sim | string | Identificador da opção |
| `texto` | sim | string | Rótulo do botão |
| `consequencias` | sim | array | Efeitos aplicados se escolhida |
| `proximo_evento` | não | string \| null | `id` do próximo evento; se omitido ou `null`, a narrativa encerra e o final é calculado |

## Condições (`condicoes[]`)

Cada item tem `tipo` e campos específicos. O evento só é elegível se **todas** passarem.

### `flag_ausente`

- `chave` (string): a flag **não** pode estar presente/verdadeira no `flags_json` do save.

### `flag_presente`

- `chave` (string): a flag deve existir e ser **verdadeira** (truthy) no `flags_json`.

### `atributo_min`

- `chave` (string): um de `energia`, `reputacao`, `networking`, `ansiedade`, `produtividade`, `aprendizado`.
- `valor` (number): valor mínimo inclusive após carregar o save.

### `atributo_max`

- `chave` (string): mesmo conjunto de atributos.
- `valor` (number): valor máximo inclusive.

Handlers adicionais devem ser registrados em `backend/app/services/conditions.py` e documentados aqui.

## Consequências (`consequencias[]`)

### `set_flag`

- `chave` (string)
- `valor` (boolean \| string \| number conforme convenção): grava no mapa de flags do save.

### `alterar_atributo`

- `chave` (string): um de `energia`, `reputacao`, `networking`, `ansiedade`, `produtividade`, `aprendizado`.
- `delta` (number): soma ao valor atual (o engine limita à faixa 0–100).

Handlers adicionais devem ser registrados em `backend/app/services/consequences.py`.

---

## Como adicionar um evento (passo a passo)

1. Abra (ou crie) um arquivo em `backend/data/events/` com o array `eventos` e acrescente o novo objeto com `id` único, `descricao`, `condicoes` e `opcoes`.
2. Garanta que o arquivo está listado em `backend/data/events/index.json` na ordem desejada (arquivos são carregados em sequência; dentro de cada arquivo, a ordem do array define a ordem de candidatos).
3. Atualize algum `proximo_evento` de opção anterior para apontar para o novo `id`, se o fluxo exigir.

Não é necessário alterar Python para apenas texto/flags/deltas **se** usar apenas tipos já suportados.
