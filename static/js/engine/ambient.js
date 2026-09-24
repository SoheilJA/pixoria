/* کیت ambient — بازیگران زمان‌محور هم‌سبک مرجع
   روز: ابر ۳لایه، خورشید ضربان‌دار، باد/برگ، پرنده V، بالون، پروانه
   شب: ستاره چشمک‌زن، ماه، شهاب، کرم شب‌تاب، خفاش
   تعامل: پارالاکس ماوس، کلیک روی زمین=وزش باد، کلیک روی پرنده=پراکندن
   همه با reduced-motion خاموش/ثابت می‌شوند */
import { RM, isDark, mulberry32 } from "../core/utils.js";
import { cachedSprite, drawSprite, Engine } from "./scene-engine.js";

export function createAmbient(opts = {}) {
  const rnd = mulberry32(opts.seed || 42);
  const state = {
    mx: 0.5,
    my: 0.5,
    gust: 0,
    birds: [],
    stars: [],
    clouds: [],
    flies: [],
    fireflies: [],
    meteors: [],
    t: 0,
  };

  const layerCount = () => (window.innerWidth < 700 ? 2 : 3);
  const cloudN = () => (window.innerWidth < 700 ? 5 : 9);
  const birdN = () => (window.innerWidth < 700 ? 2 : 5);
  const starN = () => (window.innerWidth < 700 ? 40 : 90);

  function spawnBird(burst) {
    const w = window.innerWidth,
      h = window.innerHeight;
    const y = 0.12 * h + rnd() * 0.22 * h;
    const dir = rnd() < 0.5 ? 1 : -1;
    const b = {
      x: dir > 0 ? -40 : w + 40,
      y,
      vx: dir * (18 + rnd() * 26),
      vy: (rnd() - 0.5) * 8,
      ph: rnd() * 6,
      flap: 0,
      burst: burst ? 1 : 0,
      bvy: 0,
    };
    state.birds.push(b);
    if (state.birds.length > birdN() + 6) state.birds.shift();
  }

  function spawnMeteor() {
    const w = window.innerWidth;
    state.meteors.push({
      x: rnd() * w * 0.8,
      y: rnd() * 0.25 * window.innerHeight,
      vx: 180 + rnd() * 160,
      vy: 90 + rnd() * 70,
      life: 1,
    });
    if (state.meteors.length > 3) state.meteors.shift();
  }

  function seed() {
    const w = window.innerWidth,
      h = window.innerHeight;
    state.clouds = [];
    for (let i = 0; i < cloudN(); i++) {
      const layer = i % layerCount();
      state.clouds.push({
        x: rnd() * w,
        y: (0.06 + rnd() * 0.22) * h,
        s: 14 + layer * 10 + rnd() * 10,
        v: (4 + layer * 5 + rnd() * 6) * (layer === 0 ? 1 : layer === 1 ? 0.7 : 0.45),
        a: 0.5 + layer * 0.2,
      });
    }
    state.stars = [];
    for (let i = 0; i < starN(); i++)
      state.stars.push({
        x: rnd() * w,
        y: rnd() * h * 0.6,
        ph: rnd() * 6,
        sp: 0.6 + rnd() * 1.6,
        r: rnd() < 0.12 ? 2 : 1,
      });
    state.flies = [];
    for (let i = 0; i < 6; i++)
      state.flies.push({ x: rnd() * w, y: (0.3 + rnd() * 0.4) * h, ph: rnd() * 6, vx: (rnd() - 0.5) * 30, vy: (rnd() - 0.5) * 18 });
    state.fireflies = [];
    for (let i = 0; i < 14; i++)
      state.fireflies.push({ x: rnd() * w, y: (0.35 + rnd() * 0.45) * h, ph: rnd() * 6, vx: (rnd() - 0.5) * 14, vy: (rnd() - 0.5) * 10 });
    if (!RM && !state.birdTimer) {
      state.birdTimer = setInterval(() => {
        if (document.hidden || RM) return;
        spawnBird(false);
      }, 6000 + rnd() * 5000);
      state.meteorTimer = setInterval(() => {
        if (document.hidden || RM || !isDark()) return;
        spawnMeteor();
      }, 7000);
    }
    spawnBird(false);
  }

  function drawCloud(ctx, x, y, s, a, col) {
    ctx.globalAlpha = a;
    ctx.fillStyle = col;
    const u = s;
    ctx.fillRect(x, y, u * 3, u);
    ctx.fillRect(x + u * 0.6, y - u * 0.7, u * 1.6, u * 0.8);
    ctx.fillRect(x - u * 0.5, y + u * 0.4, u * 4, u * 0.7);
    ctx.globalAlpha = 1;
  }

  function drawBird(ctx, b, day) {
    const s = 2.2;
    const spr = cachedSprite(birdSpriteKey(b.flap), birdRows(b.flap), birdPal(day), s);
    const dir = b.vx < 0 ? -1 : 1;
    ctx.save();
    ctx.translate(b.x, b.y);
    if (dir < 0) ctx.scale(-1, 1);
    drawSprite(ctx, spr, -spr.width / 2, -spr.height / 2);
    ctx.restore();
  }

  function birdRows(flap) {
    return flap
      ? ["..K....K..", ".KWK..KWK.", "KWWWKKWWWK", ".KWKWWKWK.", "..KK..KK.."]
      : ["..........", ".KWK..KWK.", "KWWWKKWWWK", ".KWKWWKWK.", "..KK..KK.."];
  }
  function birdSpriteKey(flap) {
    return "bird" + (flap ? 1 : 0);
  }
  function birdPal(day) {
    return day ? { K: "#3a3f52", W: "#f6f7fb" } : { K: "#1c2338", W: "#aab6d4" };
  }

  let mouseHandler = null,
    clickHandler = null;

  const api = {
    seed,
    attach() {
      if (RM) return;
      mouseHandler = (e) => {
        state.mx = e.clientX / window.innerWidth;
        state.my = e.clientY / window.innerHeight;
      };
      clickHandler = (e) => {
        const w = window.innerWidth,
          h = window.innerHeight;
        /* کلیک روی پرنده = پراکندن */
        let hit = false;
        for (const b of state.birds) {
          if (Math.abs(e.clientX - b.x) < 30 && Math.abs(e.clientY - b.y) < 30) {
            b.burst = 1;
            b.bvy = -60 - Math.random() * 40;
            hit = true;
          }
        }
        if (hit) api.onBurst && api.onBurst();
        /* کلیک روی نیمه‌ی پایین = وزش باد */
        else if (e.clientY > h * 0.55) state.gust = 1;
      };
      window.addEventListener("mousemove", mouseHandler, { passive: true });
      window.addEventListener("pointerdown", clickHandler, { passive: true });
    },
    detach() {
      if (mouseHandler) window.removeEventListener("mousemove", mouseHandler);
      if (clickHandler) window.removeEventListener("pointerdown", clickHandler);
      if (state.birdTimer) clearInterval(state.birdTimer);
      if (state.meteorTimer) clearInterval(state.meteorTimer);
    },
    /* eng: engine state؛ ctx: با مختصات CSS px */
    draw(eng, ctx, dt) {
      state.t += dt;
      const day = !isDark();
      const w = eng.w,
        h = eng.h;
      const px = (state.mx - 0.5) * 14,
        py = (state.my - 0.5) * 8;
      state.gust = Math.max(0, state.gust - dt * 0.5);
      const gustV = state.gust * 60;

      if (day) {
        /* خورشید + هاله‌ی ضربان‌دار */
        const sx = w * 0.82 + px * 0.4,
          sy = h * 0.16 + py * 0.4;
        const pulse = RM ? 0 : Math.sin(state.t * 1.4) * 0.06 + 1;
        ctx.fillStyle = "rgba(255,179,71,0.14)";
        ctx.beginPath();
        ctx.arc(sx, sy, 34 * pulse, 0, 7);
        ctx.fill();
        const sun = cachedSprite("sun", SUN_R, { Y: "#ffb347" }, 3);
        drawSprite(ctx, sun, sx - sun.width / 2, sy - sun.height / 2);
        /* ابرها */
        const cloudCol = "#eef2f8";
        for (const c of state.clouds) {
          c.x += (c.v + gustV) * dt;
          if (c.x > w + 120) c.x = -140;
          drawCloud(ctx, c.x + px * (0.6 - c.a * 0.5), c.y + py * 0.3, c.s, c.a, cloudCol);
        }
        /* پرنده‌ها */
        for (const b of state.birds) {
          b.flap = !b.flap;
          if (Math.floor(state.t * 4) % 2 === 0) b.flap = true;
          b.x += b.vx * dt * (1 + state.gust * 0.6);
          b.y += b.vy * dt + (b.burst ? b.bvy : 0) * dt;
          if (b.burst) b.bvy += 30 * dt;
          if (b.x < -80 || b.x > w + 80) b.dead = true;
          drawBird(ctx, b, day);
        }
        state.birds = state.birds.filter((b) => !b.dead);
        /* بالون */
        const bx = w * 0.14 + Math.sin(state.t * 0.5) * 12 + px * 0.8;
        const by = h * 0.3 + Math.sin(state.t * 0.8) * 8;
        const bal = cachedSprite("balloon", BALLOON_R, BALLOON_P, 2);
        drawSprite(ctx, bal, bx, by);
      } else {
        /* ماه */
        const mx = w * 0.82 + px * 0.4,
          my = h * 0.14 + py * 0.4;
        const moon = cachedSprite("moon", MOON_R, MOON_P, 3);
        drawSprite(ctx, moon, mx - moon.width / 2, my - moon.height / 2);
        /* ستاره‌ها */
        for (const s of state.stars) {
          const tw = RM ? 0.7 : 0.35 + 0.65 * Math.abs(Math.sin(state.t * s.sp + s.ph));
          ctx.globalAlpha = tw;
          ctx.fillStyle = "#dbe4f5";
          ctx.fillRect(s.x, s.y, s.r, s.r);
        }
        ctx.globalAlpha = 1;
        /* شهاب‌ها */
        for (const m of state.meteors) {
          m.x += m.vx * dt;
          m.y += m.vy * dt;
          m.life -= dt * 0.8;
          ctx.strokeStyle = `rgba(220,230,250,${Math.max(0, m.life)})`;
          ctx.beginPath();
          ctx.moveTo(m.x, m.y);
          ctx.lineTo(m.x - m.vx * 0.12, m.y - m.vy * 0.12);
          ctx.stroke();
        }
        state.meteors = state.meteors.filter((m) => m.life > 0);
        /* کرم شب‌تاب */
        for (const f of state.fireflies) {
          f.x += f.vx * dt;
          f.y += f.vy * dt;
          if (f.x < 0 || f.x > w) f.vx *= -1;
          if (f.y < h * 0.3 || f.y > h * 0.85) f.vy *= -1;
          const gl = RM ? 0.5 : 0.2 + 0.8 * Math.abs(Math.sin(state.t * 2 + f.ph));
          ctx.fillStyle = `rgba(190,240,140,${gl * 0.8})`;
          ctx.fillRect(f.x, f.y, 2, 2);
        }
        /* خفاش */
        for (const b of state.birds) {
          b.flap = Math.floor(state.t * 6) % 2 === 0;
          b.x += b.vx * 1.3 * dt;
          b.y += Math.sin(state.t * 3 + b.ph) * 14 * dt;
          if (b.x < -80 || b.x > w + 80) b.dead = true;
          drawBird(ctx, b, day);
        }
        state.birds = state.birds.filter((b) => !b.dead);
      }
      /* پروانه (روز) */
      if (day)
        for (const f of state.flies) {
          f.x += f.vx * dt + Math.sin(state.t * 2 + f.ph) * 20 * dt;
          f.y += f.vy * dt + Math.cos(state.t * 1.6 + f.ph) * 12 * dt;
          if (f.x < 0 || f.x > w) f.vx *= -1;
          if (f.y < h * 0.35 || f.y > h * 0.8) f.vy *= -1;
          ctx.fillStyle = RM ? "#c07b21" : Math.floor(state.t * 6) % 2 ? "#c07b21" : "#c2337a";
          ctx.fillRect(f.x, f.y, 3, 2);
          ctx.fillRect(f.x - 3, f.y, 3, 2);
        }
    },
  };

  if (!RM) api.attach();
  return api;
}

/* اسپرایت‌های ambient — ماتریس هم‌سبک مرجع */
export const SUN_R = [
  "....YY....",
  "..Y.YY.Y..",
  "...YYYY...",
  "..YYYYYY..",
  ".YYYYYYYY.",
  ".YYYYYYYY.",
  ".YYYYYYYY.",
  "..YYYYYY..",
  "...YYYY...",
  "..Y.YY.Y..",
  "....YY....",
];
export const MOON_R = [
  "....MMM....",
  "..MMMMM....",
  ".MMMM......",
  ".MMC.......",
  ".MMM.......",
  ".MMC.......",
  ".MMMM......",
  "..MMMMM....",
  "....MMM....",
];
export const MOON_P = { M: "#eaeef5", C: "#c3cbda" };
export const BALLOON_R = [
  "..KRRK..",
  ".KRRRRK.",
  "KRRYYRRK",
  "KRRYYRRK",
  ".KRRRRK.",
  "..KRRK..",
  "...KK...",
  "...KK...",
  "...KK...",
];
export const BALLOON_P = { K: "#241f1c", R: "#e2543e", Y: "#c99a2e" };
