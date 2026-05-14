import { el } from "../utils/dom.js";

const ATTR_LABELS = {
  energia: "Energia",
  reputacao: "Reputação",
  networking: "Networking",
  ansiedade: "Ansiedade",
  produtividade: "Produtividade",
  aprendizado: "Aprendizado",
};

const ATTR_ORDER = ["energia", "reputacao", "networking", "ansiedade", "produtividade", "aprendizado"];

/**
 * @param {HTMLElement} container
 * @param {Record<string, unknown> | null} save
 */
export function mountAttributesBar(container, save) {
  container.replaceChildren();

  const section = el("section", { className: "attributes panel panel--muted" });
  section.appendChild(
    el("h3", { className: "attributes__title", textContent: "Corporate Survivor — seu status" })
  );

  if (!save) {
    section.appendChild(el("p", { className: "lead", textContent: "Carregando atributos…" }));
    container.appendChild(section);
    return;
  }

  const diaRaw = save.dia_atual;
  const evRaw = save.eventos_hoje;
  const diaNum = typeof diaRaw === "number" ? diaRaw : Number(diaRaw);
  const evNum = typeof evRaw === "number" ? evRaw : Number(evRaw);
  const diaOk = Number.isFinite(diaNum) ? Math.max(1, Math.min(5, diaNum)) : 1;
  const evOk = Number.isFinite(evNum) ? Math.max(0, Math.min(3, evNum)) : 0;
  section.appendChild(
    el("p", {
      className: "attributes__progress",
      textContent: `Dia ${diaOk} de 5 · ${evOk}/3 momentos principais hoje`,
    })
  );

  for (const key of ATTR_ORDER) {
    const raw = save[key];
    const n = typeof raw === "number" ? raw : Number(raw);
    const value = Number.isFinite(n) ? Math.max(0, Math.min(100, n)) : 0;
    const label = ATTR_LABELS[key] || key;

    const extraClass =
      key === "ansiedade" ? " attr-bar--stress" : key === "energia" ? " attr-bar--energy" : "";

    const row = el("div", {
      className: `attr-bar${extraClass}`,
    });
    const head = el("div", { className: "attr-bar__head" });
    head.appendChild(el("span", { className: "attr-bar__name", textContent: label }));
    head.appendChild(el("span", { className: "attr-bar__value", textContent: String(value) }));
    row.appendChild(head);

    const track = el("div", { className: "attr-bar__track" });
    const fill = el("div", {
      className: "attr-bar__fill",
      style: `width: ${value}%`,
    });
    fill.setAttribute("role", "progressbar");
    fill.setAttribute("aria-valuemin", "0");
    fill.setAttribute("aria-valuemax", "100");
    fill.setAttribute("aria-valuenow", String(value));
    fill.setAttribute("aria-label", label);
    track.appendChild(fill);
    row.appendChild(track);

    section.appendChild(row);
  }

  container.appendChild(section);
}
