import { el } from "../utils/dom.js";

/**
 * @param {HTMLElement} container
 * @param {{
 *   evento: Record<string, unknown>;
 *   onChoose: (opcaoId: string) => void;
 *   disabled?: boolean;
 * }} opts
 */
export function mountEventScreen(container, opts) {
  container.replaceChildren();

  /** @type {string | undefined} */
  const fundo = typeof opts.evento.fundo === "string" ? opts.evento.fundo : undefined;
  const sceneClass = fundo ? `scene scene--${fundo.replace(/[^a-z0-9_]/gi, "_")}` : "scene";
  const scene = el("div", { className: sceneClass });

  /** @type {string | undefined} */
  const personagem =
    typeof opts.evento.personagem === "string" ? opts.evento.personagem : undefined;
  if (personagem) {
    const label = el("div", {
      className: "scene__label",
      textContent: `Interlocutor: ${personagem}`,
    });
    scene.appendChild(label);
  }
  container.appendChild(scene);

  const panel = el("article", { className: "panel stack" });
  const desc =
    typeof opts.evento.descricao === "string"
      ? opts.evento.descricao
      : "—";

  panel.appendChild(el("p", { className: "eyebrow", textContent: "Cena" }));
  panel.appendChild(el("h2", { className: "heading-2", textContent: desc }));

  const opcoes = Array.isArray(opts.evento.opcoes) ? opts.evento.opcoes : [];
  const list = el("ul", { className: "option-list" });

  for (const op of opcoes) {
    if (!op || typeof op !== "object") continue;
    const oid = String(/** @type {{ id?: string }} */ (op).id || "");
    const texto = String(/** @type {{ texto?: string }} */ (op).texto || oid || "Opção");
    if (!oid) continue;

    const li = el("li");
    const btn = el(
      "button",
      {
        type: "button",
        className: "option-btn",
        disabled: Boolean(opts.disabled),
      },
      [texto]
    );
    btn.addEventListener("click", () => opts.onChoose(oid));
    li.appendChild(btn);
    list.appendChild(li);
  }

  if (opcoes.length === 0) {
    panel.appendChild(el("p", { className: "lead", textContent: "Nenhuma opção disponível neste evento." }));
  } else {
    panel.appendChild(list);
  }

  container.appendChild(panel);
}
