/* =====================================================================
   HERO FIELD — موتورِ هیروی «میدانِ زنده»
   بومِ دوبعدیِ سبک: شبکهٔ نقطه‌های مربعی (موتیفِ پیکسلیِ برند) که
   نفَس میکشد، موجِ آرامی از آن میگذرد و دور نشانگرِ موش «ربایش»
   طلایی ایجاد میکند. هیچ three.js و هیچ GSAP در کار نیست.

   خودتنظیم:
   - تعداد نقطه‌ها سقف دارد (دسکتاپ ~۲۶۰۰، موبایل ~۱۵۰۰).
   - وقتی بخش از دید خارج شود یا تب پنهان شود، حلقهٔ rAF میخوابد.
   - prefers-reduced-motion: فقط یک فریمِ ساکنِ آرام رسم میشود.
   - اگر موش تکان نخورد، یک «رانندهٔ خودکار» میدان را زنده نگه میدارد.
   - hx-boost کل بدنه را جابه‌جا میکند؛ راه‌اندازیِ دوباره روی
     htmx:afterSwap انجام میشود و بومِ جداشده بلافاصله میخوابد.
   ===================================================================== */
(() => {
  "use strict";

  const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const CREAM = "245, 243, 238";
  const GOLD = "232, 196, 122";

  /* نمونه‌های فعال (بومِ هیرو + بومِ فوتر میتوانند همزمان زنده باشند) */
  const active = new Set();

  function initField(canvas) {
    const ctx = canvas.getContext("2d");
    if (!ctx || canvas.dataset.hxBound) return null;
    canvas.dataset.hxBound = "1";

    let W = 0;
    let H = 0;
    let dots = [];
    let running = false;
    let inView = true;
    let raf = 0;
    let disposed = false;
    let tHold = 0; /* زمانِ جمع‌شده در حالتِ فعال (برای انیمیشنِ پیوسته) */
    let tStartHold = 0;
    /* نشانگر: مقصد (tx/ty) و موقعیتِ نرم‌شده (x/y) */
    const P = { x: 0, y: 0, tx: 0, ty: 0, lastMove: -1e4 };

    /* ---------- ساختِ شبکه ---------- */
    function build() {
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = Math.max(1, rect.width);
      H = Math.max(1, rect.height);
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const mobile = W < 720;
      const cap = mobile ? 1500 : 2600;
      let s = mobile ? 34 : 26;
      let cols = 0;
      let rows = 0;
      for (let k = 0; k < 14; k++) {
        cols = Math.ceil(W / s) + 1;
        rows = Math.ceil(H / s) + 1;
        if (cols * rows <= cap) break;
        s *= 1.1;
      }
      const ox = (W - (cols - 1) * s) / 2;
      const oy = (H - (rows - 1) * s) / 2;

      dots = [];
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          dots.push({
            x: ox + c * s,
            y: oy + r * s,
            ph: ((c * 0.37 + r * 0.61) % 1) * Math.PI * 2,
            glow: 0,
          });
        }
      }
      if (REDUCED) draw(0);
    }

    /* ---------- رسمِ یک فریم ---------- */
    function draw(t) {
      ctx.clearRect(0, 0, W, H);
      const R = Math.min(W, H) * 0.34; /* شعاعِ تأثیرِ نشانگر */

      for (let i = 0; i < dots.length; i++) {
        const d = dots[i];

        /* نَفَسِ محیطی */
        let a = 0.055 + 0.05 * Math.sin(t * 0.55 + d.ph);
        let size = W < 720 ? 1.6 : 2;

        /* موجِ آرامِ گذرنده (عمق) */
        const sweep = Math.sin(t * 0.24 - d.x * 0.006 + d.y * 0.004);
        if (sweep > 0.86) a += 0.06 * ((sweep - 0.86) / 0.14);

        /* ربایشِ نشانگر + دنبالهٔ محوشونده */
        if (t - P.lastMove < 3.5) {
          const dx = d.x - P.x;
          const dy = d.y - P.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < R) d.glow = Math.max(d.glow, 1 - dist / R);
        }
        d.glow *= 0.945;
        if (d.glow > 0.02) {
          a = Math.min(1, a + d.glow * 0.8);
          size += d.glow * 2.4;
        }

        ctx.fillStyle =
          "rgba(" + (d.glow > 0.08 ? GOLD : CREAM) + ", " + a.toFixed(3) + ")";
        ctx.fillRect(d.x - size / 2, d.y - size / 2, size, size);
      }
    }

    /* ---------- رانندهٔ خودکار (وقتی موش ساکت است) ---------- */
    function autoTarget(t) {
      return {
        x: W / 2 + Math.sin(t * 0.23) * W * 0.32,
        y: H / 2 + Math.sin(t * 0.17 + 1.3) * H * 0.26,
      };
    }

    function elapsed() {
      return tHold + (performance.now() - tStartHold) / 1000;
    }

    /* ---------- حلقهٔ اصلی ---------- */
    function frame(now) {
      if (!running) return;
      if (!canvas.isConnected) {
        /* با hx-boost بوم جداشده است؛ حلقه بلافاصله میخوابد */
        stop();
        return;
      }
      const t = elapsed();

      /* نرمسازیِ حرکتِ نشانگر */
      let tx;
      let ty;
      if (t - P.lastMove < 3.5) {
        tx = P.tx;
        ty = P.ty;
      } else {
        const auto = autoTarget(t);
        tx = auto.x;
        ty = auto.y;
      }
      P.x += (tx - P.x) * 0.12;
      P.y += (ty - P.y) * 0.12;

      draw(t);
      raf = requestAnimationFrame(frame);
    }

    function start() {
      if (running || REDUCED || disposed) return;
      running = true;
      tStartHold = performance.now();
      raf = requestAnimationFrame(frame);
    }
    function stop() {
      if (!running) return;
      running = false;
      if (raf) cancelAnimationFrame(raf);
      tHold += (performance.now() - tStartHold) / 1000;
    }
    const onVisibility = () => {
      if (disposed) return;
      if (inView && !document.hidden) start();
      else stop();
    };

    /* ---------- رویدادها ---------- */
    /* نشانگر را روی «میزبانِ» بوم میشنویم، نه خودِ بوم؛ چون محتوا روی بوم
       قرار دارد و رویدادِ موش به بوم نمیرسد */
    const host =
      canvas.closest("section") ||
      canvas.closest("footer") ||
      canvas.parentElement;
    const onMove = (e) => {
      const r = canvas.getBoundingClientRect();
      P.tx = e.clientX - r.left;
      P.ty = e.clientY - r.top;
      if (P.lastMove < 0) {
        P.x = P.tx;
        P.y = P.ty;
      }
      P.lastMove = elapsed();
    };
    if (host && host.addEventListener) host.addEventListener("pointermove", onMove);

    let resizeTimer = 0;
    const onResize = () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(build, 180);
    };

    let io = null;
    if ("IntersectionObserver" in window) {
      io = new IntersectionObserver(
        (entries) => {
          inView = entries.some((en) => en.isIntersecting);
          onVisibility();
        },
        { rootMargin: "80px" },
      );
      io.observe(canvas);
    }

    document.addEventListener("visibilitychange", onVisibility);
    window.addEventListener("resize", onResize);
    if (host && host.addEventListener) host.addEventListener("pointermove", onMove);

    /* ---------- راه‌اندازی ---------- */
    build();
    if (REDUCED) {
      /* یک فریمِ ساکنِ آرام */
      requestAnimationFrame(() => canvas.classList.add("on"));
    } else {
      /* بوت: رانندهٔ خودکار از مرکز شروع میشود */
      P.x = W / 2;
      P.y = H / 2;
      onVisibility();
      requestAnimationFrame(() => canvas.classList.add("on"));
    }

    return {
      canvas,
      dispose() {
        if (disposed) return;
        disposed = true;
        hiddenRepaint = true;
        stop();
        if (io) io.disconnect();
        clearTimeout(resizeTimer);
        document.removeEventListener("visibilitychange", onVisibility);
        window.removeEventListener("resize", onResize);
        if (host && host.removeEventListener) host.removeEventListener("pointermove", onMove);
      },
    };
  }

  function ensure() {
    const canvases = [...document.querySelectorAll("[data-hx-field]")];
    const live = new Set(canvases);
    /* نمونههایی که بومشان از دام افتاده (hx-boost) جمع میشوند */
    for (const inst of [...active]) {
      if (!live.has(inst.canvas)) {
        inst.dispose();
        active.delete(inst);
      }
    }
    for (const cv of canvases) {
      if (cv.dataset.hxBound) continue;
      const inst = initField(cv);
      if (inst) active.add(inst);
    }
  }

  ensure();
  document.addEventListener("htmx:afterSwap", ensure);
})();
