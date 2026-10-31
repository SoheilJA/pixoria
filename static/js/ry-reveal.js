/* ry-reveal — ظاهرشدنِ تدریجیِ عناصرِ زبان طراحی Ryoku
   vanilla خالص (بدون کتابخانه): fade + جابه‌جاییِ عمودیِ کم.
   تا JS لود نشود هیچ چیز پنهان نیست (کلاسِ ry-js فقط اینجا ست می‌شود)
   و زیرِ prefers-reduced-motion همه‌چیز بی‌درنگ نمایان می‌شود. */
(function () {
  "use strict";

  var docEl = document.documentElement;
  docEl.classList.add("ry-js");

  var els = Array.prototype.slice.call(document.querySelectorAll(".ry-reveal"));
  if (!els.length) return;

  var reduce =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reduce || !("IntersectionObserver" in window)) {
    els.forEach(function (el) {
      el.classList.add("is-in");
    });
    return;
  }

  var io = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var d = parseFloat(el.getAttribute("data-delay") || "0");
        if (d > 0) el.style.setProperty("--ry-d", Math.round(d * 1000) + "ms");
        el.classList.add("is-in");
        io.unobserve(el);
      });
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
  );

  els.forEach(function (el) {
    io.observe(el);
  });
})();
