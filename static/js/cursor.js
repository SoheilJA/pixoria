/* Custom cursor — lime dot + trailing ring with contextual states.

  default        dot + thin ring
  link/button    ring tightens into a solid lime pill     (.cursor-hover)
  card/media     ring grows and shows a label             (.cursor-view)
                 label text comes from the element's `data-cursor` attribute
                 ("مشاهده" by default; carousels use "کشیدن"/"Drag")
  text input     ring becomes a caret                     (.cursor-text)
  press          dot squishes                             (.cursor-down)

A subtle pixel trail follows the pointer. Magnetic pull on CTAs is handled by
the shared data-magnetic layer (motion.js); this module only renders the cursor.

The nodes live in #cursor-shell, which is hx-preserve'd, so the cursor survives
HTMX navigations; listeners are delegated on document and re-scanned after every
swap. Disabled on touch devices and under prefers-reduced-motion.
*/
import { G, RM } from "./core/utils.js";

const FINE = matchMedia("(hover: hover) and (pointer: fine)").matches;
const TRAIL_MS = 55; /* pixel trail spawn interval */

function stateFor(target) {
  if (!target || target === document) return "";
  const view = target.closest("[data-cursor-view], .carousel, [data-cursor-label]");
  if (view) return "view";
  if (target.closest('input, textarea, select, [contenteditable="true"]')) return "text";
  if (target.closest("a, button, [data-cursor], summary, label")) return "hover";
  return "";
}

function labelFor(target) {
  if (!target) return "";
  const view =
    target.closest("[data-cursor-view], .carousel, [data-cursor-label]") || target;
  return (
    view.getAttribute("data-cursor") ||
    view.getAttribute("data-cursor-label") ||
    (view.classList && view.classList.contains("carousel") ? "کشیدن" : "مشاهده")
  );
}

export function initCursor() {
  if (!FINE || RM || !G) return;

  let shell = document.getElementById("cursor-shell");
  if (!shell) {
    shell = document.createElement("div");
    shell.id = "cursor-shell";
    shell.className = "cursor-shell";
    shell.setAttribute("hx-preserve", "");
    shell.setAttribute("aria-hidden", "true");
    const dot = document.createElement("div");
    dot.className = "cursor-dot";
    const ring = document.createElement("div");
    ring.className = "cursor-ring";
    ring.innerHTML = "<span></span>";
    shell.append(dot, ring);
    document.body.append(shell);
  }

  const dot = shell.querySelector(".cursor-dot");
  const ring = shell.querySelector(".cursor-ring");
  const label = ring.querySelector("span");

  const dotX = G.quickTo(dot, "x", { duration: 0.06 });
  const dotY = G.quickTo(dot, "y", { duration: 0.06 });
  const ringX = G.quickTo(ring, "x", { duration: 0.3, ease: "power3.out" });
  const ringY = G.quickTo(ring, "y", { duration: 0.3, ease: "power3.out" });

  let lastState = "";
  let lastTrail = 0;

  const setState = (state, text) => {
    if (state === lastState) return;
    lastState = state;
    shell.classList.remove("cursor-hover", "cursor-view", "cursor-text", "cursor-down");
    if (state) shell.classList.add("cursor-" + state);
    label.textContent = state === "view" ? text || "مشاهده" : "";
  };

  /* Delegated on document so the listeners survive HTMX body swaps. */
  window.addEventListener(
    "pointermove",
    (e) => {
      dotX(e.clientX);
      dotY(e.clientY);
      ringX(e.clientX);
      ringY(e.clientY);

      const now = performance.now();
      if (now - lastTrail > TRAIL_MS) {
        lastTrail = now;
        spawnTrail(e.clientX, e.clientY);
      }
    },
    { passive: true },
  );

  window.addEventListener(
    "pointerover",
    (e) => {
      const t = e.target;
      const state = stateFor(t);
      setState(state, state === "view" ? labelFor(t) : "");
    },
    { passive: true },
  );

  window.addEventListener("pointerdown", () => shell.classList.add("cursor-down"));
  window.addEventListener("pointerup", () => shell.classList.remove("cursor-down"));
  window.addEventListener("blur", () => setState(""));

  function spawnTrail(x, y) {
    const p = document.createElement("div");
    p.className = "cursor-trail";
    p.style.transform = `translate(${x}px, ${y}px)`;
    shell.appendChild(p);
    G.to(p, {
      scale: 0.2,
      opacity: 0,
      duration: 0.5,
      ease: "power2.out",
      onComplete: () => p.remove(),
    });
  }

  /* Cap the trail if the pointer idles long enough to pile up nodes. */
  setInterval(() => {
    const trails = shell.querySelectorAll(".cursor-trail");
    if (trails.length > 24) trails[0].remove();
  }, 2000);
}

initCursor();
document.addEventListener("htmx:afterSwap", initCursor);
