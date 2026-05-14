/**
 * Cliente HTTP da API — mesma origem que o Flask (estático + /api).
 */

const JSON_HEADERS = { "Content-Type": "application/json" };

/**
 * @param {Response} res
 * @returns {Promise<unknown>}
 */
async function parseJsonBody(res) {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return { erro: "Resposta inválida do servidor" };
  }
}

/**
 * @param {string} path
 * @param {RequestInit} [init]
 * @returns {Promise<unknown>}
 */
async function request(path, init = {}) {
  let res;
  try {
    res = await fetch(path, init);
  } catch {
    throw new Error("Sem conexão com o servidor. Verifique se o backend está em execução.");
  }
  const data = await parseJsonBody(res);
  if (!res.ok) {
    const msg =
      data && typeof data === "object" && data !== null && "erro" in data
        ? String(/** @type {{ erro: string }} */ (data).erro)
        : `Erro HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

/**
 * @param {string} nome
 * @returns {string}
 */
function encodeNomePath(nome) {
  return encodeURIComponent(nome);
}

export const api = {
  /**
   * @param {string} nome
   * @returns {Promise<{ id: number; nome: string; criado_em: string }>}
   */
  async createOrGetPlayer(nome) {
    /** @type {{ id: number; nome: string; criado_em: string }} */
    const out = /** @type {any} */ (
      await request("/api/players", {
        method: "POST",
        headers: JSON_HEADERS,
        body: JSON.stringify({ nome }),
      })
    );
    return out;
  },

  /**
   * @param {string} nome
   * @returns {Promise<Record<string, unknown>>}
   */
  async getProximoEvento(nome) {
    const q = new URLSearchParams({ nome });
    /** @type {Record<string, unknown>} */
    const out = /** @type {any} */ (await request(`/api/events/proximo?${q}`));
    return out;
  },

  /**
   * @param {string} nome
   * @param {string} eventoId
   * @param {string} opcaoId
   * @returns {Promise<Record<string, unknown>>}
   */
  async postDecision(nome, eventoId, opcaoId) {
    /** @type {Record<string, unknown>} */
    const out = /** @type {any} */ (
      await request("/api/decisions", {
        method: "POST",
        headers: JSON_HEADERS,
        body: JSON.stringify({
          nome,
          evento_id: eventoId,
          opcao_id: opcaoId,
        }),
      })
    );
    return out;
  },

  /**
   * @param {string} nome
   * @returns {Promise<Record<string, unknown>>}
   */
  async getSave(nome) {
    return /** @type {any} */ (await request(`/api/saves/${encodeNomePath(nome)}`));
  },

  /**
   * @param {string} nome
   * @returns {Promise<void>}
   */
  async deleteSave(nome) {
    await request(`/api/saves/${encodeNomePath(nome)}`, { method: "DELETE" });
  },

  /**
   * @param {number} [limite]
   * @returns {Promise<{ ranking: Record<string, unknown>[] }>}
   */
  async getRanking(limite = 20) {
    const q = new URLSearchParams({ limite: String(limite) });
    /** @type {{ ranking: Record<string, unknown>[] }} */
    const out = /** @type {any} */ (await request(`/api/ranking?${q}`));
    return out;
  },
};
