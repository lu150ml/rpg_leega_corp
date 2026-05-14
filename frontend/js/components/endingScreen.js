import { el, clear } from "../utils/dom.js";

/**
 * @param {Record<string, unknown>} row
 * @param {number} index
 */
function rowRankingEl(row, index) {
  const nome = typeof row.nome === "string" ? row.nome : "—";
  const pts = typeof row.pontuacao === "number" ? row.pontuacao : Number(row.pontuacao);
  const ptsStr = Number.isFinite(pts) ? String(pts) : "—";
  const finalId = typeof row.final_id === "string" ? row.final_id : "—";
  const tr = el("tr", {});
  tr.appendChild(el("td", { textContent: String(index + 1) }));
  tr.appendChild(el("td", { textContent: nome }));
  tr.appendChild(el("td", { textContent: ptsStr, className: "ranking-table__num" }));
  tr.appendChild(el("td", { textContent: finalId, className: "ranking-table__mono" }));
  return tr;
}

/**
 * @param {HTMLElement} container
 * @param {{
 *   final: Record<string, unknown>;
 *   metaFim: { pontuacao: number | null; posicao_ranking: number | null; ranking_top: Record<string, unknown>[] } | null;
 *   onPlayAgain: () => void;
 *   onMenu?: () => void;
 *   onRefreshRanking?: () => Promise<void>;
 *   busy?: boolean;
 *   error?: string | null;
 * }} opts
 */
export function mountEndingScreen(container, opts) {
  clear(container);

  const wrap = el("div", { className: "stack" });

  if (opts.error) {
    wrap.appendChild(el("div", { className: "alert alert--error", textContent: opts.error, role: "alert" }));
  }

  const panel = el("section", { className: "panel ending-card stack" });

  const titulo =
    typeof opts.final.titulo === "string" ? opts.final.titulo : "Fim da jornada";
  const descricao =
    typeof opts.final.descricao === "string"
      ? opts.final.descricao
      : "Sua história neste onboarding chegou ao fim.";

  panel.appendChild(el("p", { className: "eyebrow", textContent: "Final obtido" }));
  panel.appendChild(el("h2", { className: "heading-2", textContent: titulo }));
  panel.appendChild(el("p", { className: "lead", textContent: descricao }));

  const meta = opts.metaFim;
  if (meta && (meta.pontuacao != null || meta.posicao_ranking != null)) {
    const scoreBox = el("div", { className: "ending-score stack stack--tight" });
    if (meta.pontuacao != null) {
      scoreBox.appendChild(
        el("p", {
          className: "ending-score__main",
          textContent: `Pontuação final: ${meta.pontuacao}`,
        })
      );
    }
    if (meta.posicao_ranking != null) {
      scoreBox.appendChild(
        el("p", {
          className: "lead",
          textContent: `Sua posição no ranking global: ${meta.posicao_ranking}.º`,
        })
      );
    }
    panel.appendChild(scoreBox);
  }

  const top = meta?.ranking_top && meta.ranking_top.length > 0 ? meta.ranking_top : [];
  if (top.length > 0) {
    panel.appendChild(el("h3", { className: "heading-3", textContent: "Ranking global (top)" }));
    const tableWrap = el("div", { className: "ranking-table-wrap" });
    const table = el("table", { className: "ranking-table" });
    const thead = el("thead");
    const hr = el("tr");
    hr.appendChild(el("th", { textContent: "#" }));
    hr.appendChild(el("th", { textContent: "Jogador" }));
    hr.appendChild(el("th", { textContent: "Pts" }));
    hr.appendChild(el("th", { textContent: "Final" }));
    thead.appendChild(hr);
    table.appendChild(thead);
    const tbody = el("tbody");
    top.forEach((row, i) => tbody.appendChild(rowRankingEl(row, i)));
    table.appendChild(tbody);
    tableWrap.appendChild(table);
    panel.appendChild(tableWrap);
  }

  const btnRow = el("div", { className: "btn-row" });
  if (opts.onRefreshRanking) {
    const refresh = el(
      "button",
      {
        type: "button",
        className: "btn btn--ghost",
        disabled: Boolean(opts.busy),
      },
      ["Atualizar ranking"]
    );
    refresh.addEventListener("click", () => void opts.onRefreshRanking?.());
    btnRow.appendChild(refresh);
  }
  if (opts.onMenu) {
    const menu = el(
      "button",
      { type: "button", className: "btn btn--ghost", disabled: Boolean(opts.busy) },
      ["Tela inicial"]
    );
    menu.addEventListener("click", () => opts.onMenu?.());
    btnRow.appendChild(menu);
  }
  const again = el(
    "button",
    {
      type: "button",
      className: "btn btn--primary",
      disabled: Boolean(opts.busy),
    },
    ["Reiniciar jornada"]
  );
  again.addEventListener("click", () => opts.onPlayAgain());
  btnRow.appendChild(again);
  panel.appendChild(btnRow);

  wrap.appendChild(panel);

  if (opts.busy) {
    wrap.appendChild(el("p", { className: "busy-overlay", textContent: "Processando…" }));
  }

  container.appendChild(wrap);
}
