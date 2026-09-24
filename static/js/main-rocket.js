/* نقطه‌ی ورود مشترک همه‌ی صفحه‌های سینمایی */
import { $, isDark } from "./core/utils.js";
import { Sound } from "./core/sound.js";
import { initTheme, setTheme } from "./core/theme.js";
import { initSound } from "./core/controls.js";
import { initMenu } from "./core/menu.js";
import { initRail, updateRail } from "./core/rail.js";
import { initTyping } from "./core/typewriter.js";
import { initReveals } from "./core/reveal.js";
import { initPreloader } from "./core/preloader.js";
import { injectSprites } from "./core/sprites.js";
import { initSceneEngine } from "./engine/scene-engine.js";
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
  initSound();
  initMenu();
  initRail();
  initScroll();
  initTyping();
  initReveals();
  initCarousels();
  initSceneEngine();

  const story = document.body.dataset.story;
  if (story) {
    try {
      await import(`./stories/${story}.js`);
    } catch (e) {
      console.warn("story load failed:", story, e);
    }
  }

  initPreloader(() => {
    /* تایپ heroLead فقط همین‌جا — بدون تکرار (جلوگیری از صدای پیوسته) */
    const lead = $("#heroLead");
    if (lead && lead.dataset.type && !lead.dataset.done) {
      import("./core/typewriter.js").then((m) =>
        m.typeInto(lead, lead.dataset.type),
      );
    }
    if (!Sound.on) {
      setTimeout(() => {
        import("./core/toast.js").then((m) =>
          m.toast("نکته: برای صدای تایپ و بازی، SND را در نوار بالا روشن کن."),
        );
      }, 1500);
    }
  });
}

if (document.readyState === "loading")
  document.addEventListener("DOMContentLoaded", boot);
else boot();
