/* تم روز/شب — از مرجع؛ کلید مشترک بین همه‌ی صفحه‌ها */
import { $, $$, isDark, cssVar, store } from "./utils.js";
import { pixSVG, MOON_M, MOON_P, SUN_M, SUN_P } from "./sprites.js";

export let LCD = {},
  LCDSH = [];

export function refreshLCD() {
  LCD = {
    bg: cssVar("--lcd-bg"),
    ink: cssVar("--lcd-ink"),
    mid: cssVar("--lcd-mid"),
    dim: cssVar("--lcd-dim"),
  };
  LCDSH = isDark()
    ? ["#cdf08c", "#9fd66b", "#6fae4e", "#4e8a3d"]
    : ["#33302a", "#5c5748", "#847c66", "#aaa289"];
}

const listeners = [];
export function onThemeChange(fn) {
  listeners.push(fn);
}

export function setTheme(dark) {
  document.documentElement.classList.toggle("dark", dark);
  store.set("lr_theme", dark ? "dark" : "light");
  const th = $("#themeIco");
  if (th) th.innerHTML = dark ? pixSVG(MOON_M, MOON_P) : pixSVG(SUN_M, SUN_P);
  refreshLCD();
  listeners.forEach((fn) => fn(dark));
}

export function initTheme() {
  refreshLCD();
  const saved = store.get("lr_theme");
  const dark =
    saved === "dark"
      ? true
      : saved === "light"
        ? false
        : matchMedia("(prefers-color-scheme: dark)").matches;
  if (dark) document.documentElement.classList.add("dark");
  const th = $("#themeIco");
  if (th) th.innerHTML = dark ? pixSVG(MOON_M, MOON_P) : pixSVG(SUN_M, SUN_P);
  const btn = $("#btnTheme");
  if (btn) btn.addEventListener("click", () => setTheme(!isDark()));
}
