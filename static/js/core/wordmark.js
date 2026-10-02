/**
 * Pixel wordmark — assemble animation.
 *
 * The wordmark SVGs (built by scripts/build_pixel_wordmark.py) are inlined by
 * the {% pixel_wordmark %} template tag. Each pixel rect fades and drops in
 * with a random stagger on hover, and once when the first-visit preloader
 * becomes active. Fully skipped under prefers-reduced-motion.
 *
 * HTMX swaps the whole <body> (hx-boost on <body>), so this re-initializes on
 * htmx:afterSwap like the other site modules.
 */

const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)");

function play(svg) {
  const rects = svg.querySelectorAll("rect");
  rects.forEach((rect) => {
    rect.style.animation = "none";
    // Force a reflow so repeated hovers restart the animation from scratch.
    void rect.getBoundingClientRect();
    rect.style.animation = `pixel-in 0.5s ${(Math.random() * 0.4).toFixed(3)}s both`;
  });
}

export function initWordmarks(root = document) {
  if (REDUCED.matches) return;

  root.querySelectorAll(".wordmark-link .wordmark").forEach((svg) => {
    svg.addEventListener("mouseenter", () => play(svg), { passive: true });
  });

  const preloader = root.getElementById("preloader");
  const svg = preloader && preloader.querySelector(".wordmark");
  if (!svg) return;

  if (preloader.classList.contains("is-active")) {
    play(svg);
  } else {
    const observer = new MutationObserver(() => {
      if (preloader.classList.contains("is-active")) {
        play(svg);
        observer.disconnect();
      }
    });
    observer.observe(preloader, { attributes: true, attributeFilter: ["class"] });
  }
}

initWordmarks(document);
document.addEventListener("htmx:afterSwap", () => initWordmarks(document));
