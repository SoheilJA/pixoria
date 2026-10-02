/**
 * Liquid glass — cursor-following specular highlight.
 *
 * `.liquid-glass` elements expose --gx/--gy (percent position of the pointer
 * within the element) which the radial sheen pseudo-element tracks
 * (see static/src/input.css). Skipped on touch-only devices and under
 * prefers-reduced-motion.
 *
 * HTMX swaps the whole <body> (hx-boost on <body>), so this re-initializes on
 * htmx:afterSwap like the other site modules.
 */

const SKIP =
  window.matchMedia("(hover: none)").matches ||
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export function initGlass(root = document) {
  if (SKIP) return;
  root.querySelectorAll(".liquid-glass").forEach((el) => {
    if (el.dataset.glassBound) return;
    el.dataset.glassBound = "1";
    el.addEventListener("pointermove", (event) => {
      const rect = el.getBoundingClientRect();
      el.style.setProperty("--gx", `${((event.clientX - rect.left) / rect.width) * 100}%`);
      el.style.setProperty("--gy", `${((event.clientY - rect.top) / rect.height) * 100}%`);
    }, { passive: true });
  });
}

initGlass(document);
document.addEventListener("htmx:afterSwap", () => initGlass(document));
