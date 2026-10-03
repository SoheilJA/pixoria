/* موشن هدر بالای سایت — جمع‌شدن هنگام اسکرول + مگامنو خدمات
   reduced-motion: انیمیشن‌ها غیرفعال، منو همیشه قابل دسترس است */
import { RM } from "./utils.js";

const G = window.gsap || null;

export function initHeaderMotion() {
  const header = document.getElementById("site-header");
  if (!header || header.dataset.headerInit) return;
  header.dataset.headerInit = "1";

  /* ── جمع‌شدن هدر هنگام اسکرول ── */
  let lastY = window.scrollY;
  let ticking = false;

  function onScroll() {
    const y = window.scrollY;
    const shrinking = y > 24;
    header.classList.toggle("is-scrolled", shrinking);
    /* هدر مخفی هنگام اسکرول سریع به پایین */
    const hiding = y > 300 && y - lastY > 6;
    const showing = y - lastY < -6 || y < 300;
    if (hiding) header.classList.add("is-hidden");
    else if (showing) header.classList.remove("is-hidden");
    lastY = y;
    ticking = false;
  }

  window.addEventListener(
    "scroll",
    () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(onScroll);
      }
    },
    { passive: true },
  );
  onScroll();

  /* برگرداندن هدر وقتی موس روی ناحیه‌ی بالای صفحه است */
  header.addEventListener("mouseenter", () => header.classList.remove("is-hidden"));
  window.addEventListener("mousemove", (e) => {
    if (e.clientY < 40) header.classList.remove("is-hidden");
  }, { passive: true });
}
