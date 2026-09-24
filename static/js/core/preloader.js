/* پیش‌لودر — از مرجع؛ فقط اولین ورود در هر نشست (sessionStorage) */
import { $, G, RM } from "./utils.js";
import { Sound } from "./sound.js";
import { typeInto } from "./typewriter.js";

export const PRE_LINES = [
  "بوت هسته‌ی پیکسوری…",
  "اتصال به سرور خلاقیت… OK",
  "کالیبره‌ی موتورهای طراحی… OK",
  "بارگذاری خدمات و نمونه‌کارها… OK",
  "آماده‌ی پرتاب!",
];

export function initPreloader(onDone) {
  const pre = $("#pre");
  if (!pre) {
    if (onDone) onDone();
    return;
  }
  let seen = false;
  try {
    seen = sessionStorage.getItem("pixoriaPreloaded") === "1";
  } catch (e) {}
  if (seen || RM) {
    pre.remove();
    if (onDone) onDone();
    return;
  }
  try {
    sessionStorage.setItem("pixoriaPreloaded", "1");
  } catch (e) {}
  const lines = $("#preLines"),
    fill = $("#preFill"),
    start = $("#preStart");
  let i = 0,
    p = 0;
  const iv = setInterval(
    () => {
      if (i < PRE_LINES.length) {
        const d = document.createElement("div");
        d.textContent = "◆ " + PRE_LINES[i++];
        lines.appendChild(d);
        p = Math.min(88, p + 22);
      } else {
        p = 100;
        clearInterval(iv);
        start.classList.add("show");
        setTimeout(() => dismiss(false), 4200);
      }
      if (fill) fill.style.width = p + "%";
    },
    RM ? 30 : 330,
  );
  function dismiss(withSound) {
    if (!pre || pre.dataset.done) return;
    pre.dataset.done = "1";
    if (withSound) {
      Sound.ensure();
      Sound.jingle();
    }
    if (G && !RM) {
      G.to(pre, {
        opacity: 0,
        duration: 0.3,
        ease: "none",
        onComplete() {
          pre.remove();
          if (onDone) onDone();
        },
      });
    } else {
      pre.remove();
      if (onDone) onDone();
    }
  }
  start.addEventListener("click", () => dismiss(true));
  document.addEventListener(
    "keydown",
    function once() {
      if (!$("#pre")) return;
      dismiss(true);
      document.removeEventListener("keydown", once);
    },
    { once: true },
  );
}
