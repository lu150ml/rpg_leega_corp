import { api } from "./api/client.js";
import { mountAttributesBar } from "./components/attributesBar.js";
import { mountEndingScreen } from "./components/endingScreen.js";
import { mountEventScreen } from "./components/eventScreen.js";
import { mountHome } from "./components/homeScreen.js";
import { mountLogin } from "./components/login.js";
import { mountSaveControls } from "./components/saveButton.js";
import { createStore } from "./state/store.js";
import { clear, el } from "./utils/dom.js";

const store = createStore();

let hideToastTimer = 0;

/** Mostra confirmação de save automático (persistência no SQLite após cada decisão). */
function mostrarSaveAutomatico() {
  let el = document.getElementById("toast-autosave");
  if (!el) {
    el = document.createElement("div");
    el.id = "toast-autosave";
    el.className = "toast-autosave";
    el.setAttribute("role", "status");
    el.setAttribute("aria-live", "polite");
    document.body.appendChild(el);
  }
  el.textContent = "Progresso salvo automaticamente.";
  el.dataset.visible = "1";
  window.clearTimeout(hideToastTimer);
  hideToastTimer = window.setTimeout(() => {
    el.dataset.visible = "0";
  }, 3200);
}

/** @param {boolean} v */
function setAppBusy(v) {
  const app = document.getElementById("app");
  if (app) {
    app.setAttribute("aria-busy", v ? "true" : "false");
  }
}

/**
 * @param {unknown} data
 * @returns {{
 *   evento: Record<string, unknown> | null;
 *   final: Record<string, unknown> | null;
 *   pontuacao: number | null;
 *   posicao_ranking: number | null;
 *   ranking_top: Record<string, unknown>[];
 * }}
 */
function readProximoPayload(data) {
  if (!data || typeof data !== "object") {
    return {
      evento: null,
      final: null,
      pontuacao: null,
      posicao_ranking: null,
      ranking_top: [],
    };
  }
  const d = /** @type {Record<string, unknown>} */ (data);
  const evento = d.evento && typeof d.evento === "object" ? /** @type {Record<string, unknown>} */ (d.evento) : null;
  const final = d.final && typeof d.final === "object" ? /** @type {Record<string, unknown>} */ (d.final) : null;
  const pontuacao = typeof d.pontuacao === "number" ? d.pontuacao : null;
  const posicao_ranking = typeof d.posicao_ranking === "number" ? d.posicao_ranking : null;
  const ranking_top = Array.isArray(d.ranking_top)
    ? /** @type {Record<string, unknown>[]} */ (d.ranking_top)
    : [];
  return { evento, final, pontuacao, posicao_ranking, ranking_top };
}

/**
 * @param {string} nome
 */
async function loadProximo(nome) {
  const prox = await api.getProximoEvento(nome);
  const { evento, final, pontuacao, posicao_ranking, ranking_top } = readProximoPayload(prox);
  const save = /** @type {Record<string, unknown>} */ (await api.getSave(nome));

  if (final && !evento) {
    store.setState({
      phase: "ending",
      playerName: nome,
      save,
      evento: null,
      final,
      metaFim: { pontuacao, posicao_ranking, ranking_top },
      error: null,
      busy: false,
    });
    return;
  }

  if (evento) {
    store.setState({
      phase: "playing",
      playerName: nome,
      save,
      evento,
      final: null,
      metaFim: null,
      error: null,
      busy: false,
    });
    return;
  }

  store.setState({
    phase: "empty",
    playerName: nome,
    save,
    evento: null,
    final: null,
    metaFim: null,
    error: null,
    busy: false,
  });
}

/**
 * @param {string} nome
 */
async function enterGame(nome) {
  store.setState({ busy: true, error: null });
  setAppBusy(true);
  try {
    await api.createOrGetPlayer(nome);
    await loadProximo(nome);
  } catch (e) {
    store.setState({
      phase: "login",
      playerName: null,
      metaFim: null,
      error: e instanceof Error ? e.message : "Erro desconhecido",
      busy: false,
    });
  } finally {
    setAppBusy(false);
  }
}

function render() {
  const root = document.getElementById("app");
  if (!root) return;

  const state = store.getState();

  if (state.phase === "home") {
    mountHome(root, {
      onPlay: () => store.setState({ phase: "login", error: null }),
    });
    return;
  }

  if (state.phase === "login") {
    mountLogin(root, {
      onSubmit: (nome) => enterGame(nome),
      onBack: () => store.setState({ phase: "home", error: null }),
      busy: state.busy,
      error: state.error,
    });
    return;
  }

  if (state.phase === "ending" && state.final && state.playerName) {
    mountEndingScreen(root, {
      final: state.final,
      metaFim: state.metaFim,
      busy: state.busy,
      error: state.error,
      onMenu: () => store.reset(),
      onRefreshRanking: async () => {
        store.setState({ busy: true, error: null });
        setAppBusy(true);
        try {
          const data = await api.getRanking(15);
          const cur = store.getState();
          const prev = cur.metaFim;
          if (prev) {
            store.setState({
              metaFim: {
                ...prev,
                ranking_top: Array.isArray(data.ranking) ? data.ranking : [],
              },
              busy: false,
            });
          } else {
            store.setState({ busy: false });
          }
        } catch (e) {
          store.setState({
            busy: false,
            error: e instanceof Error ? e.message : "Erro ao carregar ranking",
          });
        } finally {
          setAppBusy(false);
        }
      },
      onPlayAgain: async () => {
        const nome = store.getState().playerName;
        if (!nome) return;
        store.setState({ busy: true, error: null });
        setAppBusy(true);
        try {
          await api.deleteSave(nome);
          await loadProximo(nome);
        } catch (e) {
          store.setState({
            error: e instanceof Error ? e.message : "Erro ao reiniciar",
            busy: false,
          });
        } finally {
          setAppBusy(false);
        }
      },
    });
    return;
  }

  if (state.phase === "empty" && state.playerName) {
    clear(root);
    const wrap = el("div", { className: "stack" });
    if (state.error) {
      wrap.appendChild(
        el("div", { className: "alert alert--error", textContent: state.error, role: "alert" })
      );
    }
    const panel = el("section", { className: "panel empty-state stack" });
    panel.appendChild(
      el("h2", { className: "heading-2", textContent: "Nada por aqui (ainda)" })
    );
    panel.appendChild(
      el("p", {
        className: "lead",
        textContent:
          "Não há próximo evento elegível no roteiro. Adicione capítulos em backend/data/events/ ou ajuste flags no save.",
      })
    );
    const row = el("div", { className: "btn-row" });
    const retry = el("button", { className: "btn btn--primary", type: "button" }, ["Atualizar"]);
    retry.addEventListener("click", () => {
      const nome = store.getState().playerName;
      if (nome) void loadProximo(nome);
    });
    const logout = el("button", { className: "btn btn--ghost", type: "button" }, ["Trocar jogador"]);
    logout.addEventListener("click", () => store.reset());
    row.appendChild(retry);
    row.appendChild(logout);
    panel.appendChild(row);
    wrap.appendChild(panel);
    root.appendChild(wrap);
    return;
  }

  if (state.phase === "playing" && state.evento && state.playerName) {
    clear(root);

    if (state.error) {
      root.appendChild(
        el("div", { className: "alert alert--error", textContent: state.error, role: "alert" })
      );
    }

    const layout = el("div", { className: "game-layout" });
    const attrsSlot = el("div");
    mountAttributesBar(attrsSlot, state.save);
    layout.appendChild(attrsSlot);

    const eventSlot = el("div");
    mountEventScreen(eventSlot, {
      evento: state.evento,
      disabled: state.busy,
      onChoose: async (opcaoId) => {
        const cur = store.getState();
        const nome = cur.playerName;
        const ev = cur.evento;
        if (!nome || !ev || cur.busy) return;
        const eventoId = String(ev.id || "");
        if (!eventoId) return;

        store.setState({ busy: true, error: null });
        setAppBusy(true);
        try {
          const resultado = /** @type {Record<string, unknown>} */ (
            await api.postDecision(nome, eventoId, opcaoId)
          );
          const save = /** @type {Record<string, unknown> | null} */ (
            resultado.save && typeof resultado.save === "object" ? resultado.save : null
          );
          const proxEv =
            resultado.proximo_evento && typeof resultado.proximo_evento === "object"
              ? /** @type {Record<string, unknown>} */ (resultado.proximo_evento)
              : null;
          const final =
            resultado.final && typeof resultado.final === "object"
              ? /** @type {Record<string, unknown>} */ (resultado.final)
              : null;

          if (final) {
            store.setState({
              phase: "ending",
              save,
              evento: null,
              final,
              metaFim: {
                pontuacao: typeof resultado.pontuacao === "number" ? resultado.pontuacao : null,
                posicao_ranking:
                  typeof resultado.posicao_ranking === "number" ? resultado.posicao_ranking : null,
                ranking_top: Array.isArray(resultado.ranking_top)
                  ? /** @type {Record<string, unknown>[]} */ (resultado.ranking_top)
                  : [],
              },
              busy: false,
              error: null,
            });
            mostrarSaveAutomatico();
            return;
          }

          if (proxEv) {
            store.setState({
              phase: "playing",
              save,
              evento: proxEv,
              final: null,
              metaFim: null,
              busy: false,
              error: null,
            });
            mostrarSaveAutomatico();
            return;
          }

          await loadProximo(nome);
          mostrarSaveAutomatico();
        } catch (e) {
          store.setState({
            busy: false,
            error: e instanceof Error ? e.message : "Falha ao registrar decisão",
          });
        } finally {
          setAppBusy(false);
        }
      },
    });
    layout.appendChild(eventSlot);

    const tools = el("div");
    mountSaveControls(tools, {
      busy: state.busy,
      onSync: async () => {
        const nome = store.getState().playerName;
        if (!nome) return;
        store.setState({ busy: true, error: null });
        setAppBusy(true);
        try {
          await loadProximo(nome);
        } catch (e) {
          store.setState({
            busy: false,
            error: e instanceof Error ? e.message : "Falha ao sincronizar",
          });
        } finally {
          setAppBusy(false);
        }
      },
      onReset: async () => {
        const nome = store.getState().playerName;
        if (!nome) return;
        if (!window.confirm("Reiniciar toda a jornada deste jogador? O progresso no servidor será zerado.")) {
          return;
        }
        store.setState({ busy: true, error: null });
        setAppBusy(true);
        try {
          await api.deleteSave(nome);
          await loadProximo(nome);
        } catch (e) {
          store.setState({
            busy: false,
            error: e instanceof Error ? e.message : "Falha ao reiniciar",
          });
        } finally {
          setAppBusy(false);
        }
      },
      onLogout: () => store.reset(),
    });
    layout.appendChild(tools);

    root.appendChild(layout);
    return;
  }

  store.reset();
  render();
}

store.subscribe(render);
render();
