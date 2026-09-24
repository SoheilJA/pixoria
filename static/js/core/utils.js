export const $ = (s) => document.querySelector(s);
export const $$ = (s) => [...document.querySelectorAll(s)];
export const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
export const lerp = (a, b, t) => a + (b - a) * t;
export const sstep = (p, a, b) => {
  const t = clamp((p - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
};
export const RM = matchMedia("(prefers-reduced-motion: reduce)").matches;
export const G = window.gsap || null;
if (G && window.ScrollTrigger)
  G.registerPlugin(ScrollTrigger, window.ScrollToPlugin);

export const store = {
  get(k) {
    try {
      return localStorage.getItem(k);
    } catch (e) {
      return null;
    }
  },
  set(k, v) {
    try {
      localStorage.setItem(k, v);
    } catch (e) {}
  },
};

export const isDark = () => document.documentElement.classList.contains("dark");
export const cssVar = (n) =>
  getComputedStyle(document.documentElement).getPropertyValue(n).trim();

export function hexRGB(h) {
  h = h.replace("#", "");
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ];
}

export function lerpC(c1, c2, t) {
  const a = hexRGB(c1),
    b = hexRGB(c2);
  return `rgb(${Math.round(lerp(a[0], b[0], t))},${Math.round(
    lerp(a[1], b[1], t),
  )},${Math.round(lerp(a[2], b[2], t))})`;
}

export function escapeHtml(s) {
  return String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[c],
  );
}

export function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
}

export function scrollToId(id) {
  const el = typeof id === "string" ? document.getElementById(id) : id;
  if (!el) return;
  if (G && window.ScrollToPlugin && !RM) {
    G.to(window, {
      scrollTo: { y: el, offsetY: 74 },
      duration: 0.9,
      ease: "power2.inOut",
    });
  } else el.scrollIntoView({ behavior: RM ? "auto" : "smooth" });
}

export function mulberry32(a) {
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const themeListeners = [];
export function onThemeChange(fn) {
  themeListeners.push(fn);
}
export function emitThemeChange(dark) {
  themeListeners.forEach((fn) => fn(dark));
}
