/* ظاهرشدن تدریجی سکشن‌ها — GSAP + ScrollTrigger
   data-aos markup قبلی هم با GSAP اجرا می‌شود (fade-up/down/left/right/in)
   reduced-motion: همه‌ی حرکت‌ها غیرفعال و محتوا کامل نمایش داده می‌شود */
import { $$, G, RM } from "./utils.js";

const EASE = "power2.out";

function aosVars(el) {
  const delay = parseFloat(el.dataset.aosDelay || 0) / 1000 || 0;
  const dur = parseFloat(el.dataset.aosDuration || 700) / 1000 || 0.7;
  return { delay, dur };
}

function initAosElements() {
  const els = $$("[data-aos]");
  els.forEach((el) => {
    if (el.__aosDone) return;
    el.__aosDone = true;
    const { delay, dur } = aosVars(el);
    const kind = el.dataset.aos;
    const dir = 26;
    const vars = {
      opacity: 0,
      duration: dur,
      delay,
      ease: EASE,
      scrollTrigger: { trigger: el, start: "top 90%", once: true },
    };
    if (kind === "fade-up") vars.y = dir;
    else if (kind === "fade-down") vars.y = -dir;
    else if (kind === "fade-right") vars.x = dir;
    else if (kind === "fade-left") vars.x = -dir;
    else if (kind !== "fade-in" && kind !== "zoom-in") vars.y = dir;
    if (kind === "zoom-in") vars.scale = 0.94;
    G.from(el, vars);
  });
}

export function initReveals() {
  if (!G || !window.ScrollTrigger || RM) return;

  initAosElements();

  $$(".rv")
    .filter((el) => !el.closest("#hero"))
    .forEach((el) => {
      G.from(el, {
        y: 22,
        opacity: 0,
        duration: 0.5,
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
