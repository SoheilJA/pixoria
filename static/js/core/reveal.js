/* ظاهرشدن تدریجی سکشن‌ها — از مرجع */
import { $$, G, RM } from "./utils.js";

export function initReveals() {
  if (!G || !window.ScrollTrigger || RM) return;
  $$(".rv")
    .filter((el) => !el.closest("#hero"))
    .forEach((el) => {
      G.from(el, {
        y: 22,
        opacity: 0,
        duration: 0.5,
        ease: "power2.out",
        scrollTrigger: { trigger: el, start: "top 90%", once: true },
      });
    });
  ScrollTrigger.refresh();
}
