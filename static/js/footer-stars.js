/* راه‌انداز صحنه‌ی ستاره‌ای فوتر — فقط وقتی فوتر در صفحه باشد */
async function initFooterStars() {
  const host = document.querySelector(".cfooter-stars");
  if (!host) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  try {
    const THREE = await import("./vendor/three.module.js");
    window.THREE = THREE;
    const { initFooterStars: init } = await import("./engine/footer-stars.js");
    init(host);
  } catch (e) {
    /* Three در دسترس نیست — صحنه‌ی فوتر اختیاری است */
  }
}

if (document.readyState === "loading")
  document.addEventListener("DOMContentLoaded", initFooterStars);
else initFooterStars();
