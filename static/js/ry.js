/* ry — تعاملاتِ سبکِ زبان طراحی Ryoku (vanilla خالص، بدون کتابخانه)
   فیلم‌استریپِ سکشن «درباره»: یک تصویرِ بزرگ + ردیفِ بندانگشتی‌ها +
   شمارندهٔ «01 / 04» + دکمه‌های مربعِ قبلی/بعدی. هوک‌ها data-* هستند
   (بدون id) تا کامپوننت چند بار در صفحه قابل استفاده باشد.
   پیش‌لودر: انیمیشنِ تمام‌صفحه ASCII Art، پیشرفت، گلیچ، حذف خودکار. */
(function () {
  "use strict";

  /* ---------- Filmstrip (About section) ---------- */
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

  /* ---------- Preloader (ASCII Art Full-screen) ---------- */
  function initPreloader() {
    var pl = document.getElementById("preloader");
    if (!pl) return;

    var matrix = pl.querySelector(".pl-matrix");
    var bootLines = pl.querySelectorAll(".pl-boot-line");
    var bootTexts = pl.querySelectorAll(".pl-boot-text");
    var progressBar = pl.querySelector(".pl-progress-bar");
    var progressPct = pl.querySelector(".pl-progress-pct");
    var glitch = pl.querySelector(".pl-glitch");

    /* Generate Matrix Columns */
    var chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*";
    var colCount = Math.min(30, Math.floor(window.innerWidth / 20));
    for (var i = 0; i < colCount; i++) {
      var col = document.createElement("div");
      col.className = "pl-matrix-column";
      col.style.left = (i * (100 / colCount)) + "%";
      col.style.animationDuration = (12 + Math.random() * 8) + "s";
      col.style.animationDelay = (Math.random() * 8) + "s";
      var len = 10 + Math.floor(Math.random() * 15);
      var str = "";
      for (var j = 0; j < len; j++) {
        str += chars[Math.floor(Math.random() * chars.length)];
        if (j < len - 1) str += "\n";
      }
      col.textContent = str;
      matrix.appendChild(col);
    }

    /* Boot Text Typing Animation */
    var bootIndex = 0;
    function typeNextLine() {
      if (bootIndex >= bootLines.length) {
        startProgress();
        return;
      }
      var line = bootLines[bootIndex];
      var textEl = bootTexts[bootIndex];
      var text = textEl.getAttribute("data-text") || "";
      var charIndex = 0;
      line.style.opacity = "1";
      line.style.transform = "none";

      function typeChar() {
        if (charIndex <= text.length) {
          textEl.textContent = text.substring(0, charIndex);
          charIndex++;
          setTimeout(typeChar, 30 + Math.random() * 40);
        } else {
          bootIndex++;
          setTimeout(typeNextLine, 200);
        }
      }
      typeChar();
    }

    /* Progress Bar Animation */
    function startProgress() {
      var progressBarEl = pl.querySelector(".pl-progress-bar");
      var pctEl = pl.querySelector(".pl-progress-pct");
      var duration = 2500;
      var startTime = performance.now();

      function tick(now) {
        var elapsed = now - (window._plProgressStart || now);
        if (!window._plProgressStart) window._plProgressStart = now;
        var elapsed = now - window._plProgressStart;
        var progress = Math.min(elapsed / 2500, 1);
        var width = Math.floor(progress * 100);
        var pb = pl.querySelector(".pl-progress-bar");
        if (pb) pb.style.setProperty("--pl-progress", width + "%");
        var pctEl = pl.querySelector(".pl-progress-pct");
        if (pctEl) pctEl.textContent = width + "%";

        if (progress < 1) {
          requestAnimationFrame(tick);
        } else {
          triggerGlitchAndDone();
        }
      }
      requestAnimationFrame(tick);
    }

    function triggerGlitchAndDone() {
      var glitch = document.querySelector(".pl-glitch");
      if (glitch) {
        glitch.style.animation = "none";
        glitch.offsetHeight; // reflow
        glitch.style.animation = "pl-glitch-flash 0.1s ease forwards";
      }
      setTimeout(function() {
        document.documentElement.classList.remove("has-preloader");
        var pl = document.getElementById("preloader");
        if (pl) pl.classList.add("pl-done");
        try { sessionStorage.setItem("pixoria-pl", "1"); } catch (e) {}
      }, 800);
    }

    /* Start sequence */
    setTimeout(typeNextLine, 600);
  }

  /* Initialize when DOM ready */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPreloader);
  } else {
    initPreloader();
  }
})();

/* ---------- Filmstrip (About section) ---------- */
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
