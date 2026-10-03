/* PixoriaBackground boot loader + first-visit preloader sequencing.

Reads the page's background config from `#bg-config` (a Django json_script in
base.html), boots the single canvas instance and drives the preloader:

  first visit (sessionStorage flag absent, motion allowed)
    → the canvas shows its hero state behind the pixel wordmark and a progress
      bar; when the page is loaded it tweens (pull-back + dim) into the page
      background state and the overlay fades out. Same canvas, never recreated.
  later visits / HTMX navigations
    → no preloader; the preserved canvas keeps rendering and only the scroll
      keyframes are re-scanned.

Reduced motion or no WebGL: the preloader is skipped and the CSS gradient twin
(.bg-fallback) stays as the background.
*/
import * as THREE from "../vendor/three.module.js";
import { PixoriaBackground } from "./index.js";

window.THREE = THREE;

const PRELOAD_KEY = "pixoriaPreloaded";
const RM = matchMedia("(prefers-reduced-motion: reduce)").matches;

const FA_DIGITS = ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"];
const toFa = (n) => String(Math.round(n)).replace(/\d/g, (d) => FA_DIGITS[+d]);

let bg = null;

function readConfig() {
  const el = document.getElementById("bg-config");
  if (!el) return {};
  try {
    return JSON.parse(el.textContent || "{}");
  } catch (e) {
    return {};
  }
}

function preloadUsedRecently() {
  try {
    return !!sessionStorage.getItem(PRELOAD_KEY);
  } catch (e) {
    return false;
  }
}

function markPreloaded() {
  try {
    sessionStorage.setItem(PRELOAD_KEY, "1");
  } catch (e) {}
}

/* ── First-visit preloader: progress + canvas hero state ── */
function runPreloader() {
  const pre = document.getElementById("preloader");
  if (!pre) return;
  const bar = pre.querySelector(".preloader__bar");
  const pct = pre.querySelector(".preloader__pct");

  bg.enterPreload();
  document.documentElement.classList.add("preloader-lock");
  requestAnimationFrame(() => pre.classList.add("is-active"));

  /* Real progress: the bar tracks window load, eased, with a minimum dwell so
     the wordmark's pixel assemble has time to play. */
  const startedAt = performance.now();
  const MIN_MS = RM ? 200 : 1500;
  let loaded = false;
  let progress = 0;

  const onLoad = () => {
    loaded = true;
  };
  if (document.readyState === "complete") onLoad();
  else window.addEventListener("load", onLoad, { once: true });

  const setProgress = (v) => {
    progress = v;
    if (bar) bar.style.width = `${Math.min(100, v)}%`;
    if (pct) pct.textContent = `${toFa(Math.min(100, v))}٪`;
  };

  const done = () => {
    window.removeEventListener("load", onLoad);
    document.documentElement.classList.remove("preloader-lock");
    pre.classList.remove("is-active");
    pre.classList.add("is-leaving");
    bg.exitPreload();
    markPreloaded();
    /* Keep the canvas in front until the pull-back finishes, then drop it
       behind the content and fade the overlay out. */
    setTimeout(() => {
      pre.classList.add("is-done");
      pre.classList.remove("is-leaving");
    }, RM ? 60 : 1150);
  };

  const step = () => {
    const elapsed = performance.now() - startedAt;
    const cap = loaded ? 100 : 88;
    const ease = loaded ? 0.18 : 0.06;
    setProgress(progress + (cap - progress) * ease);
    if (loaded && elapsed >= MIN_MS && progress > 99.4) {
      setProgress(100);
      done();
      return;
    }
    requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

function boot() {
  const config = readConfig();
  if (!bg) {
    bg = new PixoriaBackground();
    window.PixoriaBackground = bg;
  }
  bg.init(config);

  const firstVisit = !preloadUsedRecently();
  if (firstVisit && !RM) {
    runPreloader();
  } else {
    /* Returning visit: nothing to show, the canvas is already page-level. */
    const pre = document.getElementById("preloader");
    if (pre) pre.classList.add("is-skip");
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}

/* HTMX swaps the whole <body>; the canvas survives via hx-preserve, so only the
   scroll keyframes need rebuilding. */
document.addEventListener("htmx:afterSwap", () => {
  if (bg) bg.refresh();
});
