/* Home motion loader — only runs when the home hero is on the page.
   The hero lives in the swapped content, so this also re-inits after every
   htmx:afterSwap. */
import { initHomeMotion } from "./core/home-motion.js";

function tryInit() {
  if (!document.querySelector(".hero-title")) return;
  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", initHomeMotion);
  else initHomeMotion();
}

tryInit();

document.addEventListener("htmx:afterSwap", tryInit);
