/* موتور صحنه — نسخه‌ی عمومی از Scene مرجع
   canvas ثابت پشت محتوا، DPR≤1.5، حلقه‌ی rAF واحد، lerp اسکرول،
   کش اسپرایت روی offscreen canvas، reduced-motion = رندر ثابت */
import { $, clamp, lerp, RM, isDark, onThemeChange } from "../core/utils.js";
const engine = {
  cv: null,
  ctx: null,
  w: 0,
  h: 0,
  dpr: 1,
  p: 0,
  target: 0,
  last: 0,
  running: false,
  stories: [],
  time: 0,
};

const spriteCache = new Map();

/* کش ماتریس پیکسلی روی offscreen — به‌جای fillRect پیکسل‌به‌پیکسل در هر فریم */
export function cachedSprite(key, rows, pal, s) {
  const cacheKey = key + "|" + s + "|" + (isDark() ? "d" : "l");
  let c = spriteCache.get(cacheKey);
  if (c) return c;
  const w = Math.max(...rows.map((r) => r.length)) * s,
    h = rows.length * s;
  const off = document.createElement("canvas");
  off.width = w;
  off.height = h;
  const octx = off.getContext("2d");
  octx.imageSmoothingEnabled = false;
  for (let r = 0; r < rows.length; r++) {
    const row = rows[r];
    for (let i = 0; i < row.length; i++) {
      const col = pal[row[i]];
      if (col) {
        octx.fillStyle = col;
        octx.fillRect(i * s, r * s, s, s);
      }
    }
  }
  c = off;
  spriteCache.set(cacheKey, c);
  return c;
}

export function clearSpriteCache() {
  spriteCache.clear();
}

export function drawSprite(ctx, sprite, x, y) {
  ctx.drawImage(sprite, Math.round(x), Math.round(y));
}

export function registerStory(story) {
  engine.stories.push(story);
  if (engine.cv) story.setup && story.setup(engine);
}

function resize() {
  engine.dpr = Math.min(1.5, window.devicePixelRatio || 1);
  engine.w = window.innerWidth;
  engine.h = window.innerHeight;
  engine.cv.width = Math.round(engine.w * engine.dpr);
  engine.cv.height = Math.round(engine.h * engine.dpr);
  engine.ctx.setTransform(engine.dpr, 0, 0, engine.dpr, 0, 0);
  engine.stories.forEach((s) => s.onResize && s.onResize(engine));
}

function frame(t) {
  if (!engine.running) return;
  if (document.hidden) {
    requestAnimationFrame(frame);
    return;
  }
  const dt = Math.min(0.05, (t - engine.last) / 1000 || 0.016);
  engine.last = t;
  engine.time += dt;
  engine.p = lerp(engine.p, engine.target, 0.09);
  const ctx = engine.ctx;
  ctx.clearRect(0, 0, engine.w, engine.h);
  for (const s of engine.stories) s.draw && s.draw(engine, ctx, dt);
  requestAnimationFrame(frame);
}

function start() {
  if (engine.running || RM) {
    if (RM) {
      /* reduced-motion: یک فریم ثابت بدون حلقه */
      const ctx = engine.ctx;
      for (const s of engine.stories) s.draw && s.draw(engine, ctx, 0);
    }
    return;
  }
  engine.running = true;
  requestAnimationFrame(frame);
}

export function initSceneEngine() {
  const cv = $("#sceneCanvas");
  if (!cv) return;
  engine.cv = cv;
  engine.ctx = cv.getContext("2d");
  resize();
  window.addEventListener("resize", resize);
  onThemeChange(() => {
    clearSpriteCache();
    engine.stories.forEach((s) => s.onTheme && s.onTheme(engine));
    if (RM) {
      const ctx = engine.ctx;
      ctx.clearRect(0, 0, engine.w, engine.h);
      for (const s of engine.stories) s.draw && s.draw(engine, ctx, 0);
    }
  });
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden && !engine.running && !RM) {
      engine.running = true;
      requestAnimationFrame(frame);
    }
  });
  window.addEventListener(
    "scroll",
    () => {
      const doc = document.documentElement;
      engine.target = clamp(
        window.scrollY / Math.max(1, doc.scrollHeight - window.innerHeight),
        0,
        1,
      );
    },
    { passive: true },
  );
  start();
}

export { engine as Engine };
