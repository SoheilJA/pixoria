/* تایپ‌رایتر — بدون صدا. متن کامل در HTML است؛ انیمیشن بهبود تدریجی */
import { $$, RM } from "./utils.js";

export function typeInto(el, text, speed = 24) {
  if (el.dataset.done) return;
  el.dataset.done = "1";
  if (RM) {
    el.textContent = text;
    return;
  }
  el.textContent = "";
  let i = 0;
  el._iv = setInterval(() => {
    i++;
    el.textContent = text.slice(0, i);
    if (i >= text.length) {
      clearInterval(el._iv);
      el.textContent = text;
    }
  }, speed);
  const host =
    el.closest("section, article, details, .lift-chip, .card") ||
    el.parentElement;
  if (host)
    host.addEventListener(
      "click",
      function skip() {
        clearInterval(el._iv);
        el.textContent = text;
      },
      { once: true },
    );
}

export function initTyping() {
  const io = new IntersectionObserver(
    (ents) => {
      ents.forEach((en) => {
        if (!en.isIntersecting) return;
        io.unobserve(en.target);
        typeInto(en.target, en.target.dataset.type);
      });
    },
    { threshold: 0.3 },
  );
  $$("[data-type]").forEach((el) => io.observe(el));
  $$("#faq details").forEach((d) => {
    d.addEventListener("toggle", () => {
      if (d.open) {
        const p = d.querySelector("p");
        if (p && p.dataset.type) {
          p.dataset.done = "";
          typeInto(p, p.dataset.type);
        }
      }
    });
  });
}
