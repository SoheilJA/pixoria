/* داستان خانه — «پرتاب تا فرود»: موشک، فضا، فرود؛ فازها روی پیشرفت اسکرول */
import { $, RM, isDark, clamp, sstep } from "../core/utils.js";
import { Engine, registerStory, cachedSprite, drawSprite, clearSpriteCache } from "../engine/scene-engine.js";
import { createAmbient, SUN_R, MOON_R, MOON_P } from "../engine/ambient.js";

const ROCKET_R = [
  ".....RR.....",
  "....RRRR....",
  "....WWWW....",
  "...WWWWWW...",
  "...WWWWWW...",
  "..WWWWWWWW..",
  "..WWWWWWWW..",
  ".WWWWWWWWWW.",
  ".WWGGGGGGWW.",
  ".WWGGGGGGWW.",
  ".WWWWWWWWWW.",
  ".WWWWWWWWWW.",
  ".WWRWWWWRWW.",
  ".WWWWWWWWWW.",
  ".WWWWWWWWWW.",
  "WW.WWWWWW.WW",
  "WWW.WWWW.WWW",
  "RWW.WWWW.WWR",
  "RR.WW..WW.RR",
  "RR.DDDDDD.RR",
  "....DDDD....",
  "....DDDD....",
  ".....DD.....",
];
const ROCKET_P = { R: "#e2543e", W: "#f4f6fb", G: "#9adfff", D: "#6a7390" };
const AST_R = [
  "...KKKK...",
  "..KWWWWK..",
  "..KWGGWK..",
  "..KWGGWK..",
  "...KWWK...",
  "..KWWWWK..",
  ".WKWWWWKW.",
  ".WKWWWWKW.",
  "..KWWWWK..",
  "..KAWWAK..",
  "..KWWWWK..",
  "..KW..WK..",
  "..KW..WK..",
  "..KK..KK..",
];
const AST_P = { K: "#141a3a", W: "#f2f5fb", G: "#8fd8ff", A: "#e2543e" };

/* فازها روی پیشرفت اسکرول: 0 پرتاب، .12-.45 فضا، .45-.55 ورود اتمسفر، .55-.85 فرود، .85+ پایگاه */
const story = {
  id: "home",
  ambient: null,
  planets: [
    { p0: 0.2, p1: 0.3, r: 26, hue: "#c99a2e" },
    { p0: 0.27, p1: 0.37, r: 18, hue: "#1f8fa8" },
    { p0: 0.36, p1: 0.46, r: 34, hue: "#9c3f66" },
  ],
  setup() {
    this.ambient = createAmbient({ seed: 7 });
    this.ambient.seed();
    this.ambient.onBurst = () => {};
    if (!window.__onScrollProgress)
      window.__onScrollProgress = () => {};
  },
  onResize() {
    if (this.ambient) this.ambient.seed();
  },
  onTheme() {},
  draw(eng, ctx, dt) {
    const w = eng.w,
      h = eng.h,
      p = eng.p,
      day = !isDark();
    ctx.imageSmoothingEnabled = false;
    this.ambient.draw(eng, ctx, dt);

    /* --- آسمان به فضا --- */
    const space = sstep(p, 0.08, 0.3);
    if (space > 0 || !day) {
      const night = day ? space : 1;
      ctx.fillStyle = `rgba(6,10,24,${night * 0.92})`;
      ctx.fillRect(0, 0, w, h);
    }

    if (p < 0.5) {
      /* --- پرتاب: زمین/سکو --- */
      const lift = sstep(p, 0.02, 0.16);
      const groundY = h * 0.88 + lift * h * 0.5;
      ctx.fillStyle = day ? "#7d9a5f" : "#243a2c";
      ctx.fillRect(0, groundY, w, h - groundY);
      ctx.fillStyle = day ? "#5c7a46" : "#1a2c20";
      ctx.fillRect(0, groundY, w, 8);
      /* برج پرتاب */
      ctx.fillStyle = day ? "#6b7386" : "#3a4460";
      ctx.fillRect(w * 0.3, groundY - 70, 10, 70);
      /* شعله‌ی موشک هنگام پرتاب */
      const thrust = sstep(p, 0.02, 0.1) * (1 - sstep(p, 0.2, 0.3));
      /* --- موشک: مسیر از سکو به فضا و بازگشت به فرود --- */
      const rx = w * (0.5 - Math.sin(p * Math.PI * 1.2) * 0.18);
      const ry =
        p < 0.45
          ? h * 0.85 - sstep(p, 0.02, 0.45) * h * 1.1
          : h * 0.85 - (1 - sstep(p, 0.45, 0.8)) * h * 1.1;
      const scale = 3 + sstep(p, 0.05, 0.45) * 1.5 - sstep(p, 0.45, 0.8) * 2;
      const rk = cachedSprite("rocket", ROCKET_R, ROCKET_P, Math.max(2, scale));
      /* چرخش ملایم در بازگشت */
      ctx.save();
      ctx.translate(rx, ry);
      const tilt = p < 0.45 ? Math.sin(p * 6) * 0.03 : -0.25 * sstep(p, 0.45, 0.55);
      ctx.rotate(tilt);
      drawSprite(ctx, rk, -rk.width / 2, -rk.height / 2);
      if (thrust > 0.05) {
        ctx.fillStyle = `rgba(255,150,60,${0.5 + Math.random() * 0.4})`;
        const fl = 14 + Math.random() * 16 * thrust * scale;
        ctx.fillRect(-4 * scale, rk.height / 2, 8 * scale, fl);
      }
      ctx.restore();
      /* --- سیاره‌ها در فضا --- */
      for (const pl of this.planets) {
        const a = sstep(p, pl.p0, pl.p1) * (1 - sstep(p, pl.p1, pl.p1 + 0.06));
        if (a <= 0) continue;
        const px = w * 0.75 - (pl.p0 * w * 0.4),
          py = h * (0.2 + pl.p0 * 0.5);
        ctx.globalAlpha = a;
        ctx.fillStyle = pl.hue;
        ctx.beginPath();
        ctx.arc(px + Math.sin(pl.p0 * 20) * 40, py, pl.r, 0, 7);
        ctx.fill();
        ctx.fillStyle = "rgba(0,0,0,0.18)";
        ctx.beginPath();
        ctx.arc(px + Math.sin(pl.p0 * 20) * 40 + pl.r * 0.3, py + pl.r * 0.2, pl.r * 0.8, 0, 7);
        ctx.fill();
        ctx.globalAlpha = 1;
      }
      /* --- ستاره‌های فضا (روی آسمان تیره) --- */
      if (space > 0.2) {
        ctx.fillStyle = `rgba(230,238,255,${(space - 0.2) * 1.2})`;
        for (let i = 0; i < 40; i++) {
          const sx = ((i * 97) % 100) / 100 * w;
          const sy = ((i * 53) % 100) / 100 * h * 0.8;
          ctx.fillRect(sx, sy, 2, 2);
        }
      }
    } else {
      /* --- فرود و پایگاه --- */
      const land = sstep(p, 0.45, 0.62);
      const groundY = h * 0.8;
      ctx.fillStyle = day ? "#8a7a5f" : "#2c2838";
      ctx.fillRect(0, groundY, w, h - groundY);
      ctx.fillStyle = day ? "#6b5c46" : "#221e2c";
      ctx.fillRect(0, groundY, w, 6);
      /* پایگاه */
      ctx.fillStyle = day ? "#c8cdd8" : "#3c4258";
      ctx.fillRect(w * 0.15, groundY - 26, 46, 26);
      ctx.fillStyle = day ? "#8fa4c4" : "#28304a";
      ctx.fillRect(w * 0.15 + 8, groundY - 18, 8, 8);
      ctx.fillRect(w * 0.15 + 24, groundY - 18, 8, 8);
      /* فضانورد کنار پایگاه بعد از فرود */
      const astA = sstep(p, 0.75, 0.85);
      if (astA > 0) {
        ctx.globalAlpha = astA;
        const ak = cachedSprite("ast", AST_R, AST_P, 2);
        drawSprite(ctx, ak, w * 0.3, groundY - ak.height - 4);
        ctx.globalAlpha = 1;
      }
      /* موشک فرودآمده */
      const rk = cachedSprite("rocket", ROCKET_R, ROCKET_P, 2);
      const landY = groundY - rk.height + (1 - land) * -h * 0.6;
      drawSprite(ctx, rk, w * 0.55, landY);
      /* گرد و غبار فرود */
      if (land > 0 && land < 1) {
        ctx.fillStyle = `rgba(180,160,120,${(1 - land) * 0.5})`;
        ctx.beginPath();
        ctx.arc(w * 0.55 + rk.width / 2, groundY, 40 + land * 60, Math.PI, 0);
        ctx.fill();
      }
    }
  },
};

export function initHomeStory() {
  registerStory(story);
  /* کنسول آرکید فقط وقتی در DOM باشد */
  if ($("#arcade")) {
    import("../arcade/console.js").then((m) => m.default.init());
  }
}
initHomeStory();
