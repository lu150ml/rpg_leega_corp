/**
 * Estado mínimo com pub/sub para coordenar componentes sem framework.
 * @typedef {{
 *   phase: 'home' | 'login' | 'playing' | 'ending' | 'empty';
 *   playerName: string | null;
 *   save: Record<string, unknown> | null;
 *   evento: Record<string, unknown> | null;
 *   final: Record<string, unknown> | null;
 *   metaFim: { pontuacao: number | null; posicao_ranking: number | null; ranking_top: Record<string, unknown>[] } | null;
 *   error: string | null;
 *   busy: boolean;
 * }} GameState
 */

/** @type {GameState} */
const initialState = {
  phase: "home",
  playerName: null,
  save: null,
  evento: null,
  final: null,
  metaFim: null,
  error: null,
  busy: false,
};

/**
 * @returns {{ getState: () => GameState; setState: (p: Partial<GameState>) => void; subscribe: (fn: () => void) => () => void; reset: () => void }}
 */
export function createStore() {
  /** @type {GameState} */
  let state = { ...initialState };
  /** @type {Set<() => void>} */
  const listeners = new Set();

  function notify() {
    listeners.forEach((fn) => fn());
  }

  return {
    getState() {
      return state;
    },
    /**
     * @param {Partial<GameState>} patch
     */
    setState(patch) {
      state = { ...state, ...patch };
      notify();
    },
    /**
     * @param {() => void} fn
     * @returns {() => void}
     */
    subscribe(fn) {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
    reset() {
      state = { ...initialState };
      notify();
    },
  };
}
