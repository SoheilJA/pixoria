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
      return { ...base, y: 0, autoAlpha: 1, skewY: 0, filter: "blur(0px)", duration: Math.max(dur, 0.9) };
    case "blind":
      return { ...base, y: 0, autoAlpha: 1, clipPath: "inset(-2% -2% -2% -2%)", duration: Math.max(dur, 0.7), ease: "power4.out" };
    case "clip":
      return { ...base, clipPath: "inset(0% 0% 0% 0% round 8px)", scale: 1, autoAlpha: 1, filter: "blur(0px)", duration: Math.max(dur, 0.9), ease: "power2.out" };
    case "stagger-card":
      return { ...base, y: 0, autoAlpha: 1, rotateX: 0, duration: Math.max(dur, 0.75) };
    default:
      return { ...base, y: 0, autoAlpha: 1, filter: "blur(0px)", duration: Math.max(dur, 0.75) };
  }
}

function initAosElements() {
  const els = $$("[data-aos]").filter((el) => !el.__aosDone);
  if (!els.length) return;

  /* المان‌های داخل کاروسل را انیمیت نمی‌کنیم — با ترنسفورم والد تداخل دارد */
  const animatable = els.filter((el) => !el.closest(".carousel-track"));
  els.forEach((el) => (el.__aosDone = true));

  /* کارت‌های هم‌خانواده با stagger گروهی */
  const groups = new Map();
  animatable.forEach((el) => {
    const { delay, dur } = aosVars(el);
    const kind = el.dataset.aos;
    if (kind === "fade-in") {
      G.fromTo(el, { autoAlpha: 0 }, { autoAlpha: 1, duration: dur, delay, ease: EASE, immediateRender: false, scrollTrigger: { trigger: el, start: "top 95%", once: true } });
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
      vars.immediateRender = false;
      G.fromTo(el, { ...stateFor(variant, kind) }, vars);
    }
  });

  groups.forEach((items, parent) => {
    const targets = items.map((i) => i.el);
    const durs = Math.max(...items.map((i) => i.dur));
    G.fromTo(targets,
      { y: 38, autoAlpha: 0, rotateX: 5, transformOrigin: "50% 100%", filter: "blur(4px)" },
      {
        y: 0, autoAlpha: 1, rotateX: 0, filter: "blur(0px)",
        duration: Math.max(durs, 0.8),
        ease: EASE,
        immediateRender: false,
        stagger: { each: 0.09, from: "start" },
        scrollTrigger: { trigger: parent, start: "top 92%", once: true },
      });
  });
}

/* حالت اولیه‌ی هر واریانت برای fromTo */
function stateFor(variant, kind) {
  switch (variant) {
    case "headline": return { y: 46, autoAlpha: 0, skewY: 3, filter: "blur(8px)" };
    case "blind": return { y: 18, autoAlpha: 0, clipPath: "inset(0 0 100% 0)" };
    case "clip": return { clipPath: "inset(12% 8% 12% 8% round 8px)", scale: 1.04, autoAlpha: 0, filter: "blur(6px)" };
    case "stagger-card": return { y: 36, autoAlpha: 0, rotateX: 6, transformOrigin: "50% 100%" };
    default:
      if (kind === "fade-down") return { y: -30, autoAlpha: 0 };
      if (kind === "fade-right") return { x: 34, autoAlpha: 0 };
      if (kind === "fade-left") return { x: -34, autoAlpha: 0 };
      return { y: 32, autoAlpha: 0, filter: "blur(4px)" };
  }
}

/* تور ایمنی: هر المانی که بعد از لود کامل هنوز مخفی ماند، نمایان می‌شود */
function installSafetyNet() {
  const show = () => {
    $$("[data-aos], .rv").forEach((el) => {
      if (el.__aosDone) return;
      el.__aosDone = true;
      G.set(el, { clearProps: "all", autoAlpha: 1 });
    });
    ScrollTrigger.refresh();
  };
  window.addEventListener("load", () => setTimeout(show, 1200));
  setTimeout(show, 4000);
}

export function initReveals() {
  if (!G || !window.ScrollTrigger || RM) return;

  initAosElements();

  $$(".rv")
    .filter((el) => !el.closest("#hero") && !el.closest(".carousel-track"))
    .forEach((el) => {
      G.fromTo(el,
        { y: 24, autoAlpha: 0 },
        {
          y: 0, autoAlpha: 1, duration: 0.6, ease: EASE, immediateRender: false,
          scrollTrigger: { trigger: el, start: "top 95%", once: true },
        });
    });

  ScrollTrigger.refresh();
  installSafetyNet();

  /* محتوای جدید htmx هم انیمیت شود — روی document ثبت می‌شود
     چون htmx با hx-boost کل body را جایگزین می‌کند */
  document.addEventListener("htmx:afterSwap", () => {
    initAosElements();
    ScrollTrigger.refresh();
  });
}
