/* ظاهرشدن تدریجی سکشن‌ها — GSAP + ScrollTrigger
   data-aos markup قبلی هم با GSAP اجرا می‌شود
   انیمیشن‌های متنوع: fade/blind/blur/clip/skew + stagger گروهی
   reduced-motion: همه‌ی حرکت‌ها غیرفعال و محتوا کامل نمایش داده می‌شود */
import { $$, G, RM } from "./utils.js";

const EASE = "power3.out";

function aosVars(el) {
  const delay = (parseFloat(el.dataset.aosDelay || 0) || 0) / 1000;
  const dur = (parseFloat(el.dataset.aosDuration || 700) || 700) / 1000;
  return { delay, dur };
}

/* انتخاب نسخه‌ی انیمیشن بر اساس نقش المان — نه فقط فید ساده */
function pickVariant(el) {
  const cls = el.className || "";
  if (/hero-title|\bh1\b|text-hero/.test(cls)) return "headline";
  if (/svc-card|work-card|article|group/.test(cls) && el.parentElement?.children.length > 2) return "stagger-card";
  if (/eyebrow|font-mono/.test(cls)) return "blind";
  if (/img|aspect-/.test(cls)) return "clip";
  return "rise";
}

function varsFor(variant, { dur, delay }) {
  const base = { duration: dur, delay, ease: EASE, scrollTrigger: { trigger: null, start: "top 90%", once: true } };
  switch (variant) {
    case "headline":
      return { ...base, y: 46, opacity: 0, skewY: 3, filter: "blur(8px)", duration: Math.max(dur, 0.9) };
    case "blind":
      return { ...base, y: 18, opacity: 0, clipPath: "inset(0 0 100% 0)", duration: Math.max(dur, 0.7), ease: "power4.out" };
    case "clip":
      return { ...base, clipPath: "inset(12% 8% 12% 8% round 8px)", scale: 1.04, filter: "blur(6px)", duration: Math.max(dur, 0.9), ease: "power2.out" };
    case "stagger-card":
      return { ...base, y: 36, opacity: 0, rotateX: 6, transformOrigin: "50% 100%", duration: Math.max(dur, 0.75) };
    default:
      return { ...base, y: 32, opacity: 0, filter: "blur(4px)", duration: Math.max(dur, 0.75) };
  }
}

function initAosElements() {
  const els = $$("[data-aos]").filter((el) => !el.__aosDone);
  if (!els.length) return;

  /* کارت‌های هم‌خانواده با stagger گروهی */
  const groups = new Map();
  els.forEach((el) => {
    el.__aosDone = true;
    const { delay, dur } = aosVars(el);
    const kind = el.dataset.aos;
    if (kind === "fade-in") {
      G.from(el, { opacity: 0, duration: dur, delay, ease: EASE, scrollTrigger: { trigger: el, start: "top 90%", once: true } });
      return;
    }
    const parent = pickVariant(el) === "stagger-card" ? el.parentElement : null;
    if (parent && !groups.has(parent)) groups.set(parent, []);
    if (parent) groups.get(parent).push({ el, delay, dur });
    else {
      const variant = pickVariant(el);
      const vars = varsFor(variant, { dur, delay });
      /* جهت‌ها برای سازگاری با data-aos قبلی */
      if (kind === "fade-down") vars.y = -30;
      else if (kind === "fade-right") { vars.x = 34; vars.y = 0; }
      else if (kind === "fade-left") { vars.x = -34; vars.y = 0; }
      vars.scrollTrigger.trigger = el;
      G.from(el, vars);
    }
  });

  groups.forEach((items, parent) => {
    const targets = items.map((i) => i.el);
    const durs = Math.max(...items.map((i) => i.dur));
    G.from(targets, {
      y: 38,
      opacity: 0,
      rotateX: 5,
      transformOrigin: "50% 100%",
      filter: "blur(4px)",
      duration: Math.max(durs, 0.8),
      ease: EASE,
      stagger: { each: 0.09, from: "start" },
      scrollTrigger: { trigger: parent, start: "top 88%", once: true },
    });
  });
}

export function initReveals() {
  if (!G || !window.ScrollTrigger || RM) return;

  initAosElements();

  $$(".rv")
    .filter((el) => !el.closest("#hero"))
    .forEach((el) => {
      G.from(el, {
        y: 24,
        opacity: 0,
        duration: 0.6,
        ease: EASE,
        scrollTrigger: { trigger: el, start: "top 90%", once: true },
      });
    });

  ScrollTrigger.refresh();

  /* محتوای جدید htmx هم انیمیت شود */
  document.body.addEventListener("htmx:afterSwap", () => {
    initAosElements();
    ScrollTrigger.refresh();
  });
}
