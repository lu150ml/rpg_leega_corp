/**
 * Pequenos utilitários de DOM para montar a UI sem framework.
 * @param {string} tag
 * @param {Record<string, string | boolean | null | undefined>} [attrs]
 * @param {(string | Node)[]} [children]
 * @returns {HTMLElement}
 */
export function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, val] of Object.entries(attrs)) {
    if (val === undefined || val === null || val === false) continue;
    if (key === "className") node.className = String(val);
    else if (key === "textContent") node.textContent = String(val);
    else if (key === "htmlFor") node.setAttribute("for", String(val));
    else if (key === "disabled") node.disabled = Boolean(val);
    else if (key === "value" && "value" in node) node.value = String(val);
    else node.setAttribute(key, String(val));
  }
  for (const child of children) {
    if (typeof child === "string") node.appendChild(document.createTextNode(child));
    else if (child) node.appendChild(child);
  }
  return node;
}

/**
 * @param {HTMLElement} node
 */
export function clear(node) {
  while (node.firstChild) {
    node.removeChild(node.firstChild);
  }
}

/**
 * @param {HTMLElement} root
 * @param {HTMLElement | null} previous
 * @param {HTMLElement} next
 */
export function patchChild(root, previous, next) {
  if (previous && previous.parentNode === root) {
    root.replaceChild(next, previous);
  } else {
    root.appendChild(next);
  }
  return next;
}
