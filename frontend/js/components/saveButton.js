import { el } from "../utils/dom.js";

/**
 * @param {HTMLElement} container
 * @param {{
 *   onSync: () => void;
 *   onReset: () => void;
 *   onLogout: () => void;
 *   busy?: boolean;
 * }} opts
 */
export function mountSaveControls(container, opts) {
  container.replaceChildren();

  const toolbar = el("div", { className: "toolbar" });

  const syncBtn = el(
    "button",
    {
      type: "button",
      className: "btn btn--ghost",
      disabled: Boolean(opts.busy),
    },
    ["Recarregar do servidor"]
  );
  syncBtn.addEventListener("click", () => opts.onSync());

  const hint = el("p", {
    className: "text-muted text-small",
    textContent:
      "Cada escolha grava o progresso automaticamente no banco (save automático). Use os botões abaixo apenas se precisar atualizar a tela, zerar a jornada ou trocar de jogador.",
  });

  const resetBtn = el(
    "button",
    {
      type: "button",
      className: "btn btn--danger",
      disabled: Boolean(opts.busy),
    },
    ["Reiniciar jornada"]
  );
  resetBtn.addEventListener("click", () => opts.onReset());

  const logoutBtn = el(
    "button",
    {
      type: "button",
      className: "btn btn--ghost",
      disabled: Boolean(opts.busy),
    },
    ["Trocar jogador"]
  );
  logoutBtn.addEventListener("click", () => opts.onLogout());

  const wrap = el("div", { className: "stack stack--tight" });
  wrap.appendChild(hint);
  wrap.appendChild(toolbar);
  toolbar.appendChild(syncBtn);
  toolbar.appendChild(resetBtn);
  toolbar.appendChild(logoutBtn);
  container.appendChild(wrap);
}
