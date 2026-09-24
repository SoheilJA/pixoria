/* راه‌انداز موشن — فقط وقتی هیروی خانه در صفحه باشد */
import { initHomeMotion } from "./core/motion.js";

if (document.querySelector(".hero-title")) {
  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", initHomeMotion);
  else initHomeMotion();
}
