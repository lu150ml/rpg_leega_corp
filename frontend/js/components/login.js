import { clear, el } from "../utils/dom.js";

/**
 * @param {HTMLElement} container
 * @param {{ onSubmit: (nome: string) => void; onBack?: () => void; busy?: boolean; error?: string | null }} opts
 */
export function mountLogin(container, opts) {
  clear(container);

  const wrap = el("div", { className: "stack" });

  if (opts.error) {
    wrap.appendChild(el("div", { className: "alert alert--error", textContent: opts.error, role: "alert" }));
  }

  const panel = el("section", { className: "panel stack" });
  panel.appendChild(el("p", { className: "eyebrow", textContent: "Corporate Survivor" }));
  panel.appendChild(el("h2", { className: "heading-2", textContent: "Cadastro — como podemos te chamar?" }));
  panel.appendChild(
    el("p", {
      className: "lead",
      textContent:
        "Seu nome identifica o perfil no servidor. Use o mesmo nome para retomar o trainee no ponto em que parou; um nome novo começa outra jornada do primeiro dia.",
    })
  );

  const form = el("form", { className: "stack stack--tight" });
  const idInput = "campo-nome-jogador";
  form.appendChild(el("label", { className: "form-label", htmlFor: idInput, textContent: "Nome" }));
  const input = el("input", {
    className: "text-input",
    id: idInput,
    name: "nome",
    type: "text",
    autocomplete: "username",
    maxlength: "80",
    required: "required",
    "aria-required": "true",
    disabled: Boolean(opts.busy),
  });
  form.appendChild(input);

  const btnRow = el("div", { className: "btn-row" });
  if (opts.onBack) {
    const back = el("button", { className: "btn btn--ghost", type: "button", disabled: Boolean(opts.busy) }, [
      "Voltar",
    ]);
    back.addEventListener("click", () => opts.onBack && opts.onBack());
    btnRow.appendChild(back);
  }
  const submitBtn = el(
    "button",
    {
      className: "btn btn--primary",
      type: "submit",
      disabled: Boolean(opts.busy),
    },
    ["Entrar"]
  );
  btnRow.appendChild(submitBtn);
  form.appendChild(btnRow);

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const nome = String(input.value || "").trim();
    if (!nome) return;
    opts.onSubmit(nome);
  });

  panel.appendChild(form);
  wrap.appendChild(panel);

  if (opts.busy) {
    wrap.appendChild(el("p", { className: "busy-overlay", textContent: "Conectando…" }));
  }

  container.appendChild(wrap);
  input.focus();
}
