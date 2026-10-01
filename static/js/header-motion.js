/* راه‌انداز موشن هدر بالای سایت */
import { initHeaderMotion } from "./core/header.js";

function tryInit() {
  if (!document.getElementById("site-header")) return;
  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", initHeaderMotion);
  else initHeaderMotion();
}

tryInit();

/* htmx: بعد از جابجایی صفحه، هدر دوباره راه می‌افتد.
   روی document ثبت می‌شود چون htmx با hx-boost کل body را جایگزین می‌کند. */
document.addEventListener("htmx:afterSwap", tryInit);
