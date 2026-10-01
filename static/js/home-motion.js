/* راه‌انداز موشن — فقط وقتی هیروی خانه در صفحه باشد */
import { initHomeMotion } from "./core/motion.js";

function tryInit() {
  if (!document.querySelector(".hero-title")) return;
  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", initHomeMotion);
  else initHomeMotion();
}

tryInit();

/* htmx: وقتی به صفحه‌ی خانه برمی‌گردیم، موشن هیرو دوباره راه می‌افتد.
   روی document ثبت می‌شود چون htmx با hx-boost کل body را جایگزین می‌کند. */
document.addEventListener("htmx:afterSwap", tryInit);
