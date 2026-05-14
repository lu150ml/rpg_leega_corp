import { clear, el } from "../utils/dom.js";

/**
 * @param {HTMLElement} container
 * @param {{ onPlay: () => void }} opts
 */
export function mountHome(container, opts) {
  clear(container);

  const wrap = el("div", { className: "stack" });
  const panel = el("section", { className: "panel panel--hero stack" });
  panel.appendChild(el("p", { className: "eyebrow", textContent: "Trainee — semana 1" }));
  panel.appendChild(el("h2", { className: "heading-2", textContent: "Bem-vindo ao Corporate Survivor" }));
  panel.appendChild(
    el("p", {
      className: "lead",
      textContent:
        "Você entra como trainee no primeiro dia. São cinco dias úteis, com três momentos de decisão em cada um. Escolhas alteram seus atributos e o desfecho da história — e ao encerrar, sua pontuação entra no ranking global.",
    })
  );

  const btnRow = el("div", { className: "btn-row" });
  const play = el(
    "button",
    { type: "button", className: "btn btn--primary" },
    ["Cadastrar nome e jogar"]
  );
  play.addEventListener("click", () => opts.onPlay());
  btnRow.appendChild(play);
  panel.appendChild(btnRow);
  wrap.appendChild(panel);
  container.appendChild(wrap);
}
