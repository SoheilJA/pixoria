/* ry — تعاملاتِ سبکِ زبان طراحی Ryoku (vanilla خالص، بدون کتابخانه)
   فیلم‌استریپِ سکشن «درباره»: یک تصویرِ بزرگ + ردیفِ بندانگشتی‌ها +
   شمارندهٔ «01 / 04» + دکمه‌های مربعِ قبلی/بعدی. هوک‌ها data-* هستند
   (بدون id) تا کامپوننت چند بار در صفحه قابل استفاده باشد. */
(function () {
  "use strict";

  function initFilmstrip(root) {
    var main = root.querySelector("[data-ry-main]");
    var link = root.querySelector("[data-ry-link]");
    var caption = root.querySelector("[data-ry-caption]");
    var counter = root.querySelector("[data-ry-counter]");
    var thumbs = Array.prototype.slice.call(root.querySelectorAll("[data-ry-thumb]"));
    if (!main || !thumbs.length) return;

    var i = 0;
    function pad(n) {
      return (n < 10 ? "0" : "") + n;
    }

    function show(idx) {
      i = (idx + thumbs.length) % thumbs.length;
      var t = thumbs[i];
      thumbs.forEach(function (el, k) {
        el.classList.toggle("is-active", k === i);
        el.setAttribute("aria-pressed", k === i ? "true" : "false");
      });
      var src = t.getAttribute("data-full");
      if (src) main.src = src;
      var label = t.getAttribute("data-label") || "";
      main.alt = label;
      if (link) link.href = t.getAttribute("data-href") || link.href;
      if (caption) caption.textContent = label;
      if (counter) counter.textContent = pad(i + 1) + " / " + pad(thumbs.length);
    }

    thumbs.forEach(function (el, k) {
      el.addEventListener("click", function () {
        show(k);
      });
    });

    var prev = root.querySelector("[data-ry-prev]");
    var next = root.querySelector("[data-ry-next]");
    if (prev) prev.addEventListener("click", function () { show(i - 1); });
    if (next) next.addEventListener("click", function () { show(i + 1); });

    show(0);
  }

  document.querySelectorAll("[data-ry-filmstrip]").forEach(initFilmstrip);
})();
