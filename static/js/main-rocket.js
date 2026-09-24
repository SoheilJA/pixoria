/* نقطه‌ی ورود مشترک همه‌ی صفحه‌ها — بدون صدا */
import { $ } from "./core/utils.js";
import { initTheme, setTheme } from "./core/theme.js";
import { initMenu } from "./core/menu.js";
import { initRail, updateRail } from "./core/rail.js";
import { initTyping } from "./core/typewriter.js";
import { initReveals } from "./core/reveal.js";
import { injectSprites } from "./core/sprites.js";
import { initCarousels } from "./core/carousel.js";

function initScroll() {
  const apply = () => {
    const doc = document.documentElement;
    const p = Math.max(
      0,
      Math.min(
        1,
        window.scrollY / Math.max(1, doc.scrollHeight - window.innerHeight),
      ),
    );
    updateRail(p);
    window.__sceneTarget = p;
    if (window.__onScrollProgress) window.__onScrollProgress(p);
  };
  window.addEventListener("scroll", apply, { passive: true });
  apply();
}

async function boot() {
  injectSprites();
  initTheme();
  initMenu();
  initRail();
  initScroll();
  initTyping();
  initReveals();
  initCarousels();

  /* هدر موبایل: باز/بستن منوی تمام‌صفحه */
  const mtBtn = $("#btnMenu"),
    mtNav = $("#mobile-nav"),
    mtClose = $("#menuClose");
  if (mtBtn && mtNav) {
    const open = () => {
      mtNav.classList.add("open");
      mtBtn.setAttribute("aria-expanded", "true");
    };
    const close = () => {
      mtNav.classList.remove("open");
      mtBtn.setAttribute("aria-expanded", "false");
    };
    mtBtn.addEventListener("click", open);
    if (mtClose) mtClose.addEventListener("click", close);
    mtNav.querySelectorAll("a").forEach((a) => a.addEventListener("click", close));
  }

  const story = document.body.dataset.story;
  if (story) {
    try {
      await import(`./stories/${story}.js`);
    } catch (e) {
      console.warn("story load failed:", story, e);
    }
  }

  /* تایپ heroLead */
  const lead = $("#heroLead");
  if (lead && lead.dataset.type && !lead.dataset.done) {
    import("./core/typewriter.js").then((m) =>
      m.typeInto(lead, lead.dataset.type),
    );
  }
}

if (document.readyState === "loading")
  document.addEventListener("DOMContentLoaded", boot);
else boot();
