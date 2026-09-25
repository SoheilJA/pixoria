/* راه‌انداز ظاهرشدن data-aos با GSAP — برای قالب‌های غیر سینمایی */
import { initReveals } from "./core/reveal.js";

if (document.readyState === "loading")
  document.addEventListener("DOMContentLoaded", initReveals);
else initReveals();
