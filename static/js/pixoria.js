/**
 * Pixoria — shared interaction layer (v2 design).
 *
 * Ported from the inline script of new/index.html. Handles smooth scroll,
 * scroll-driven reveals/counters, magnetic + tilt effects, the mobile menu,
 * scroll progress, the testimonial slider, the portfolio filter, marquee
 * duplication, the process GPS draw, the FAQ accordion, the toast and the blog
 * article chrome (reading-progress bar, table-of-contents highlight, copy-link button).
 *
 * Loaded as an ES module from base.html. هیچ GSAP ای در پروژه نیست: کل حرکت با
 * CSS (static/css/motion.css) انجام می‌شود و این ماژول فقط ماشه می‌زند —
 * کلاسِ is-in با IntersectionObserver، متغیرهای CSS برای مکانِ اشاره‌گر و
 * مسیرِ GPS، و شمارشِ اعداد. هر ویژگی روی دستگاهِ ضعیف، حالتِ
 * prefers-reduced-motion و ورودیِ لمسی نرم عقب می‌نشیند.
 * Lenis به‌صورت ماژول وارد می‌شود، پس هیچ گلوبالی لازم نیست.
 */

import Lenis from "./vendor/lenis.js";

const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
const TOUCH = matchMedia("(hover: none)").matches;

const FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹";
const faDigits = (value) => String(value).replace(/\d/g, (d) => FA_DIGITS[d]);

/* ------------------------------------------------------- CSS-var helpers
   هیچ انیمیشنِ جاوااسکریپتی در پروژه نیست؛ این ماژول فقط ماشه می‌زند و
   متغیرهای CSS را ست می‌کند و خودِ حرکت در static/css/motion.css اجرا
   می‌شود. تنها استثنا، دو تابعِ عددیِ زیر است که مقدارِ نهایی را به‌صورت
   متن (با ارقامِ فارسی) می‌شمارند — چون CSS نمی‌تواند عدد را فرمت کند. */

const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);
const easeOutExpo = (t) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t));

// شمارندهٔ سبک بر پایهٔ requestAnimationFrame (جایگزینِ gsap.to روی اعداد).
function tweenNumbers(duration, onUpdate, { from = 0, to = 1, ease = easeOutCubic } = {}) {
  const t0 = performance.now();
  const step = (now) => {
    const p = Math.min(1, (now - t0) / duration);
    onUpdate(from + (to - from) * ease(p));
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

/* ------------------------------------------------------------------ toast */

let toastTimer = null;

function showToast(msg) {
  const toast = document.getElementById("toast");
  const text = document.getElementById("toast-text");
  if (!toast || !text) return;
  text.textContent = msg;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 4200);
}
// Exposed so templates/HTMX flows (contact form) can fire it.
window.pixoriaToast = showToast;

/* ------------------------------------------------------------------ init */

function init() {
  // پرچمِ «ماژول بالا آمد» — تورِ اطمینانِ <head> با همین بررسی می‌کند که
  // اگر ماژول هرگز اجرا نشد، حالتِ پنهانِ انیمیشن‌ها کنار گذاشته شود.
  window.__pixoriaBooted = true;

  /* ---------------- smooth scroll (Lenis) ----------------
     روی دستگاه‌های کم‌توان اسکرولِ نرم را کامل رد می‌کنیم: Lenis هر فریم به
     main thread وابسته است و همان چیزی است که روی سخت‌افزار ضعیف «گیر» حس
     می‌شود. بدون آن، اسکرول بومی مرورگر است و انیمیشن‌ها سر جایشان می‌مانند.
     حلقهٔ رفرش را خودمان با rAF می‌چرخانیم (قبلاً روی ticker گسپ سوار بود). */
  const LOW_POWER =
    (navigator.hardwareConcurrency || 8) <= 4 ||
    (navigator.deviceMemory || 8) <= 4;
  let lenis = null;
  if (!REDUCED && !LOW_POWER) {
    lenis = new Lenis({ duration: 0.9, smoothWheel: true });
    const raf = (time) => {
      lenis.raf(time);
      requestAnimationFrame(raf);
    };
    requestAnimationFrame(raf);
  } else {
    document.documentElement.style.scrollBehavior = "smooth";
  }

  /* ---------------- mobile menu v3 (delegated) ----------------
     کلِ <body> با hx-boost تعویض میشود؛ به همین دلیل «هیچ» لیسنری روی
     عناصرِ خودِ منو نمیچسبد. رویدادها یک بار روی document وصل میشوند و
     در هر کلیک، DOMِ زنده پرسوجو میشود — پس پس از هر ناوبری هم
     همبرگر، دکمهٔ بستن و آکاردئون سالم میمانند. */
  const openMobileMenu = () => {
    const menu = document.getElementById("mobile-menu");
    if (!menu || menu.classList.contains("open")) return;
    menu.classList.add("open");
    document.getElementById("menu-open")?.setAttribute("aria-expanded", "true");
    // قفلِ اسکرول روی <html> (کلاس) + body و متوقفکردنِ lenis؛ هر سه در
    // close آزاد میشوند و htmx:afterSwap هم اهرمِ ترمیمِ مستقل دارد.
    document.documentElement.classList.add("nav-lock");
    document.body.style.overflow = "hidden";
    if (lenis) lenis.stop();
    menu.querySelector(".mm-close")?.focus({ preventScroll: true });
  };
  const closeMobileMenu = () => {
    const menu = document.getElementById("mobile-menu");
    if (!menu || !menu.classList.contains("open")) return;
    menu.classList.remove("open");
    document.getElementById("menu-open")?.setAttribute("aria-expanded", "false");
    menu.querySelectorAll("[data-m-accordion]").forEach((btn) => {
      btn.setAttribute("aria-expanded", "false");
      btn.closest("li")?.classList.remove("m-sub-open");
    });
    document.documentElement.classList.remove("nav-lock");
    document.body.style.overflow = "";
    if (lenis) lenis.start();
    document.getElementById("menu-open")?.focus({ preventScroll: true });
  };
  document.addEventListener("click", (e) => {
    const t = e.target;
    if (!(t instanceof Element) || !t.closest) return;
    if (t.closest("#menu-open")) {
      openMobileMenu();
      return;
    }
    if (t.closest("[data-menu-close]")) {
      closeMobileMenu();
      return;
    }
    const acc = t.closest("[data-m-accordion]");
    if (acc) {
      const open = acc.getAttribute("aria-expanded") === "true";
      acc.setAttribute("aria-expanded", String(!open));
      acc.closest("li")?.classList.toggle("m-sub-open", !open);
      return;
    }
    if (t.closest("#mobile-menu a[href]")) closeMobileMenu();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeMobileMenu();
  });
  // اهرمِ ترمیم: هر تعویضِ htmx منو را میبندد و قفلِ اسکرول را آزاد میکند
  // (اگر کاربر با منوی باز ناوبری کرده باشد، صفحه هرگز گیرِ قفل نمیماند).
  document.addEventListener("htmx:afterSwap", closeMobileMenu);

  /* ---------------- mega menu (services dropdown) ----------------
     باز شدن با هاور (با تأخیرِ کوچک در بستن) و با کلیک/کیبورد روی چورون.
     روی صفحات لمسی فقط کلیدزار عمل می‌کند. */
  document.querySelectorAll("[data-mega-root]").forEach((root) => {
    const toggle = root.querySelector("[data-mega-toggle]");
    if (!toggle) return;
    let closeTimer = null;
    const setOpen = (open) => {
      clearTimeout(closeTimer);
      root.classList.toggle("open", open);
      toggle.setAttribute("aria-expanded", String(open));
    };
    if (!TOUCH) {
      root.addEventListener("mouseenter", () => setOpen(true));
      root.addEventListener("mouseleave", () => {
        closeTimer = setTimeout(() => setOpen(false), 300);
      });
    }
    toggle.addEventListener("click", () =>
      setOpen(toggle.getAttribute("aria-expanded") !== "true"),
    );
    root.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && root.classList.contains("open")) {
        setOpen(false);
        toggle.focus();
      }
    });
    // بستن وقتی焦点 از کل مجموعه خارج می‌شود
    root.addEventListener("focusout", (e) => {
      if (!root.contains(e.relatedTarget)) setOpen(false);
    });
    // بستن پس از کلیک روی یکی از کاشی‌ها
    root.querySelectorAll(".mega-menu a").forEach((a) =>
      a.addEventListener("click", () => setOpen(false)),
    );
  });

  /* ---------------- anchor links ---------------- */
  const scrollToEl = (el) => {
    if (lenis) lenis.scrollTo(el, { offset: -96, duration: 1.2 });
    else el.scrollIntoView({ behavior: REDUCED ? "auto" : "smooth" });
  };
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      if (id.length > 1) {
        const el = document.querySelector(id);
        if (el) {
          e.preventDefault();
          closeMobileMenu();
          scrollToEl(el);
        }
      }
    });
  });

  /* ---------------- scroll progress + navbar state ---------------- */
  const bar = document.getElementById("scroll-progress");
  const navEl = document.querySelector("#site-header nav");
  const navLinks = [...document.querySelectorAll("#site-header .nav-link")];
  const syncActiveNav = () => {
    // Nav items are real page URLs, so "active" follows the current path.
    const path = location.pathname.replace(/\/+$/, "") || "/";
    navLinks.forEach((a) => {
      let linkPath;
      try {
        linkPath = new URL(a.href, location.origin).pathname.replace(/\/+$/, "") || "/";
      } catch {
        return;
      }
      a.classList.toggle("active", linkPath === path);
    });
  };
  const onScroll = () => {
    const h = document.documentElement;
    const p = h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight);
    if (bar) bar.style.transform = `scaleX(${p})`;
    if (navEl) navEl.classList.toggle("nav-solid", h.scrollTop > 40);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  onScroll();
  syncActiveNav();
  document.addEventListener("htmx:pushedIntoHistory", syncActiveNav);
  document.addEventListener("htmx:afterSettle", syncActiveNav);

  /* ---------------- page-transition loader (T54) ----------------
     ناوبریِ سایت کاملاً چندصفحه‌ایست (hx-boost حذف شده — D15)؛ htmx فقط برای
     تعویضِ محتوای بلاگ و فرم تماس است. پس ماشهٔ اصلی، کلیک روی لینک‌های
     هم‌مبدأ است. نوار به مدتِ کوتاهی دیده نمی‌شود (~۱۵۰ms تأخیر) و سیارهٔ
     مداری فقط اگر ناوبری طولانی شد (~۴۰۰ms). هرگز صفحه را نمی‌پوشاند. */
  const navBar = document.getElementById("nav-progress");
  const navOrbit = document.getElementById("nav-orbit");
  if (navBar) {
    const bar = navBar.querySelector(".nav-progress-bar");
    let startTimer = null;
    let orbitTimer = null;
    let failsafe = null;
    let rafId = null;
    let progress = 0;
    let active = false;

    const reset = () => {
      cancelAnimationFrame(rafId);
      rafId = null;
      clearTimeout(startTimer);
      clearTimeout(orbitTimer);
      clearTimeout(failsafe);
      startTimer = orbitTimer = failsafe = null;
    };
    const stop = () => {
      reset();
      if (!active) return;
      active = false;
      if (bar) bar.style.transform = "";
      navBar.classList.add("done"); // پرش به ۱۰۰٪
      navOrbit.classList.remove("show");
      setTimeout(() => {
        navBar.classList.remove("show", "done");
        if (bar) bar.style.transform = "scaleX(0)";
      }, 500);
    };

    // خزیدنِ آرامِ نوار به سمت ~۹۲٪ (هرگز ۱۰۰٪ تا اتمام ناوبری)
    const crawl = () => {
      const tick = () => {
        progress += (0.92 - progress) * 0.035;
        if (bar) bar.style.transform = `scaleX(${progress})`;
        rafId = requestAnimationFrame(tick);
      };
      tick();
    };

    const start = () => {
      if (active) return;
      active = true;
      progress = 0;
      // ناوبری‌های سریع اصلاً چیزی نشان داده نمی‌شود
      startTimer = setTimeout(() => {
        navBar.classList.add("show");
        if (REDUCED) {
          // حرکت کاهشی: نوار ایستا، بدون سیارهٔ چرخان
          if (bar) bar.style.transform = "scaleX(0.35)";
        } else {
          crawl();
          orbitTimer = setTimeout(
            () => navOrbit.classList.add("show"),
            400 - 150,
          );
        }
      }, 150);
      // هرگز بیش از ۱۰ ثانیه روی صفحه نمانَد (ناوبریِ گیرکرده)
      failsafe = setTimeout(stop, 10000);
    };

    // تکمیل/مخفی شدن
    document.addEventListener("htmx:afterSettle", stop);
    document.addEventListener("htmx:responseError", stop);
    document.addEventListener("htmx:sendError", stop);
    window.addEventListener("pageshow", (e) => {
      if (e.persisted) stop(); // بازگشت از bfcache
    });
    window.addEventListener("pagehide", stop);

    // ماشهٔ htmx: فقط درخواست‌هایی که تاریخچه را جابه‌جا می‌کنند (boost /
    // push-url). درخواست‌های فعلیِ پروژه (فیلتر/بیشترِ بلاگ، فرم تماس) ناوبری
    // نیستند → نادیده گرفته می‌شوند.
    document.addEventListener("htmx:beforeRequest", (e) => {
      const cfg = e.detail?.requestConfig || {};
      const elt = e.detail?.elt || cfg.elt || null;
      const navigates =
        cfg.boosted ||
        cfg.pushUrl === true ||
        (elt &&
          elt.hasAttribute &&
          (elt.hasAttribute("hx-push-url") ||
            !!elt.closest("[hx-push-url]")));
      if (navigates) start();
    });

    // ماشهٔ کلیک روی لینک‌های معمولیِ هم‌مبدأ
    document.addEventListener("click", (e) => {
      if (e.defaultPrevented || e.button !== 0) return;
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      const a = e.target.closest?.("a[href]");
      if (!a) return;
      // لینک‌های مدیریت‌شده توسط htmx را htmx هندل می‌کند
      if (a.closest("[hx-get],[hx-post],[hx-boost]")) return;
      if (a.target && a.target !== "_self" && a.target !== "_top" && a.target !== "_parent")
        return;
      if (a.hasAttribute("download")) return;
      const href = a.getAttribute("href");
      if (!href || href.startsWith("#") || href.startsWith("mailto:") || href.startsWith("tel:"))
        return;
      let url;
      try {
        url = new URL(a.href, location.origin);
      } catch {
        return;
      }
      if (url.origin !== location.origin) return;
      if (url.pathname === location.pathname && url.search === location.search) return;
      start();
    });
  }

  /* ---------------- reveal animations ----------------
     ماشه فقط یک کلاس است؛ خودِ حرکت در motion.css تعریف شده. JS سه کار
     می‌کند: ۱) شمارهٔ پلکانِ هر عنصر را در --rv-i می‌گذارد تا ردیف‌ها
     پشتِ‌سرِ‌هم برسند، ۲) data-delay (ثانیه — مثل قبل) را به متغیرِ CSS
     ترجمه می‌کند، ۳) تورِ اطمینان که در بدترین حالت کلاسِ نهایی را مستقیم
     می‌گذارد تا هیچ محتوایی پنهان نماند. */
  const indexReveals = () => {
    document.querySelectorAll("[data-reveal]").forEach((el) => {
      if (el.dataset.rvIndexed === "1") return;
      el.dataset.rvIndexed = "1";
      if (el.dataset.delay) {
        el.style.setProperty(
          "--rv-delay",
          `${Math.round(parseFloat(el.dataset.delay) * 1000)}ms`,
        );
      }
      const parent = el.parentElement;
      if (!parent) return;
      const kin = [...parent.children].filter((c) =>
        c.hasAttribute("data-reveal"),
      );
      const i = kin.indexOf(el);
      if (kin.length > 1 && i > 0) el.style.setProperty("--rv-i", Math.min(i, 9));
    });
  };

  const revealEl = (el) => {
    if (el.dataset.revealDone === "1") return;
    el.dataset.revealDone = "1";
    if (REDUCED) {
      el.classList.add("is-in");
      return;
    }
    const settle = () => el.classList.add("is-in");
    const safety = onContentTimeout(settle, el);
    onceIntersecting(el, () => {
      // یک بازخوانیِ layout تا مرورگر حالتِ اولیه را «دیده» باشد؛ وگرنه
      // مرورگر ممکن است هر دو حالت را در یک فریم ببیند و پرش کند.
      void el.offsetWidth;
      requestAnimationFrame(() => {
        el.classList.add("is-in");
        const done = () => clearSafety(safety);
        el.addEventListener("transitionend", done, { once: true });
        setTimeout(done, 2800);
      });
    });
  };
  let revealsStarted = false;
  const initReveals = () => {
    revealsStarted = true;
    indexReveals();
    document.querySelectorAll("[data-reveal]").forEach(revealEl);
  };

  /* ---------------- first-visit preloader ----------------
     هماهنگی با پیش‌لودرِ base.html: CSS خودش تا ~۱.۲۵ ثانیه دیگر المان را
     محو می‌کند؛ اینجا زودتر، به‌محض آماده شدن صفحه، آن را برمی‌داریم.
     انیمیشن‌های ورود (data-reveal) تا آن لحظه صبر می‌کنند تا زیرِ پردهٔ
     محوشونده وارد شوند — نه قبل از آن. */
  const preloader = document.getElementById("preloader");
  // فقط در اولین بارگزاریِ session — وگرنه المان display:none است و نیازی به
  // هماهنگی نیست (reveals فوراً شروع می‌شوند).
  const hasPreloader =
    preloader && document.documentElement.classList.contains("has-preloader");
  if (hasPreloader && !REDUCED) {
    let done = false;
    const hide = () => {
      if (done) return;
      done = true;
      initReveals();
      // اگر CSS از قبل المان را محو کرده، فقط گره‌ش را جمع می‌کنیم (راه‌اندازی
      // دوبارهٔ انیمیشن = فلش)
      if (parseFloat(getComputedStyle(preloader).opacity) < 0.1) {
        preloader.remove();
        return;
      }
      preloader.classList.add("pl-done");
      setTimeout(() => preloader.remove(), 500);
    };
    const navStart = performance.getEntriesByType("navigation")[0]?.startTime ?? 0;
    if (document.readyState === "complete") {
      // صفحه زود آماده شده (احتمالاً از کش) — برند خیلی کوتاه دیده شود
      setTimeout(hide, 300);
    } else {
      window.addEventListener(
        "load",
        () => {
          // لودِ سریع → خودمان زودتر برمی‌داریم؛ لودِ کند → CSS جریان دارد
          if (performance.now() - navStart < 700) setTimeout(hide, 150);
        },
        { once: true },
      );
    }
    // لود کند: انیمیشن‌های ورود هم‌زمان با شروعِ محوشدنِ CSS (۰.۸ ثانیه)
    setTimeout(() => {
      if (!done) initReveals();
    }, 800);
    // failsafe: گرهٔ DOM هرگز بیش از ۱.۶ ثانیه باقی نمی‌ماند
    setTimeout(hide, 1600);
  } else {
    initReveals();
  }
  // تعویضِ HTMX → فقط عناصرِ تازه‌اضافه‌شده آنیمیشن می‌گیرند (با رعایت
  // prefers-reduced-motion).
  document.addEventListener("htmx:afterSettle", () => {
    if (REDUCED) return;
    document.querySelectorAll("[data-blog-reveal]").forEach((el) => {
      if (el.dataset.revealDone) return;
      indexReveals();
      revealEl(el);
      if (!TOUCH) tiltCard(el);
    });
  });
  // hx-boost کلِ <body> را عوض می‌کند؛ پس هر عنصرِ تازه هم باید دوباره ماشه
  // بگیرد، وگرنه پشتِ حالتِ پنهانِ CSS (html.motion) جا می‌ماند و صفحه
  // «خالی» به نظر می‌رسد.
  document.addEventListener("htmx:afterSwap", () => {
    initReveals();
    if (!TOUCH && !REDUCED) {
      document.querySelectorAll("[data-tilt]").forEach(tiltCard);
    }
  });

  /* ---------------- counters (data-counter) ---------------- */
  document.querySelectorAll("[data-counter]").forEach((el) => {
    const target = +el.dataset.counter;
    const fmt = (v) =>
      (el.dataset.prefix || "") +
      v.toLocaleString("fa-IR") +
      (el.dataset.suffix || "");
    if (REDUCED) {
      el.textContent = fmt(target);
      return;
    }
    el.textContent = fmt(0);
    onContentTimeout(() => {
      el.textContent = fmt(target);
    }, el);
    onceIntersecting(el, () =>
      tweenNumbers(
        1800,
        (v) => {
          el.textContent = fmt(Math.round(v));
        },
        { to: target, ease: easeOutExpo },
      ),
    );
  });

  /* ---------------- مغناطیسی (دکمه‌ها و چیپ‌های CTA) ----------------
     JS فقط مکانِ اشاره‌گر را در متغیرهای CSS می‌گذارد؛ خودِ کشش و بازگشت
     را ترنزیشنِ CSS در motion.css انجام می‌دهد. */
  if (!TOUCH && !REDUCED) {
    document.querySelectorAll("[data-magnetic]").forEach((btn) => {
      btn.addEventListener(
        "pointermove",
        (e) => {
          const r = btn.getBoundingClientRect();
          btn.style.setProperty(
            "--mg-x",
            `${((e.clientX - r.left - r.width / 2) * 0.3).toFixed(1)}px`,
          );
          btn.style.setProperty(
            "--mg-y",
            `${((e.clientY - r.top - r.height / 2) * 0.35).toFixed(1)}px`,
          );
        },
        { passive: true },
      );
      btn.addEventListener("pointerleave", () => {
        btn.style.setProperty("--mg-x", "0px");
        btn.style.setProperty("--mg-y", "0px");
      });
    });
  }

  /* ---------------- 3D tilt cards + glare ----------------
     چرخشِ سه‌بعدی با متغیرهای --tx/--ty در CSS اجرا می‌شود و برقِ گوشهٔ
     کارت هم با --gx/--gy؛ JS هیچ ترنزیشنی نمی‌سازد. */
  const tiltCard = (card) => {
    if (card.dataset.tiltReady === "1") return;
    card.dataset.tiltReady = "1";
    card.addEventListener(
      "pointermove",
      (e) => {
        const r = card.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width;
        const py = (e.clientY - r.top) / r.height;
        card.style.setProperty("--tx", `${((py - 0.5) * -6).toFixed(2)}deg`);
        card.style.setProperty("--ty", `${((px - 0.5) * 6).toFixed(2)}deg`);
        card.style.setProperty("--gx", px * 100 + "%");
        card.style.setProperty("--gy", py * 100 + "%");
      },
      { passive: true },
    );
    card.addEventListener("pointerleave", () => {
      card.style.setProperty("--tx", "0deg");
      card.style.setProperty("--ty", "0deg");
    });
  };
  if (!TOUCH && !REDUCED) {
    document.querySelectorAll("[data-tilt]").forEach(tiltCard);
  }

  /* ---------------- floating elements ----------------
     شناوریِ تزئینی کاملاً در CSS است (keyframes rvFloat)؛ JS فقط دامنه و
     تأخیرِ نامنظم را می‌گذارد تا هیچ دو عنصری هم‌زمان شناور نشوند. */
  if (!REDUCED) {
    document
      .querySelectorAll("[data-float], [data-float-spin]")
      .forEach((el) => {
        const amp = parseFloat(el.dataset.float || el.dataset.floatSpin || "10");
        el.style.setProperty("--float-amp", `${amp}px`);
        el.style.setProperty("--float-dur", `${(2.8 + Math.random() * 2.2).toFixed(2)}s`);
        el.style.setProperty("--float-delay", `${(-Math.random() * 2.4).toFixed(2)}s`);
        el.style.setProperty("--float-spin", `${(18 + Math.random() * 18).toFixed(1)}s`);
      });
  }

  /* ---------------- pause decorative animations off-screen ----------
     المان‌های تزئینیِ متحرک (مثل سامانهٔ خورشیدیِ هیرویِ درباره ما) با
     data-pause نشانه‌گذاری می‌شوند؛ وقتی از دید خارج شدند انیمیشنشان متوقف
     می‌شود تا CPU/GPU بیکار بماند (animation-play-state در input.css). */
  document.querySelectorAll("[data-pause]").forEach((el) => {
    if (!("IntersectionObserver" in window)) return;
    new IntersectionObserver(
      (entries) => {
        el.classList.toggle("is-paused", !entries[0].isIntersecting);
      },
      { rootMargin: "120px" },
    ).observe(el);
  });

  /* ---------------- hero mouse parallax ---------------- */
  // هر سکشن هیرو (خانه یا درباره ما) که data-mouse-parallax داشته باشد.
  if (!TOUCH && !REDUCED) {
    document.querySelectorAll("[data-mouse-parallax]").forEach((hero) => {
      const layers = hero.querySelectorAll("[data-depth]");
      hero.addEventListener(
        "mousemove",
        (e) => {
          const cx = e.clientX / innerWidth - 0.5;
          const cy = e.clientY / innerHeight - 0.5;
          layers.forEach((el) => {
            const d = parseFloat(el.dataset.depth) * 120;
            el.style.transform = `translate(${(cx * d).toFixed(1)}px, ${(cy * d).toFixed(1)}px)`;
          });
        },
        { passive: true },
      );
    });
  }

  initSliders({ REDUCED, faDigits });
  initCarousels({ REDUCED, faDigits });
  initPortfolioFilter({ REDUCED, faDigits });
  initMarquees();
  initStatCounts();
  initStatCountText();
  initBuildBars();
  initGpsDraw({ REDUCED });
  initFaq();
  initArticleChrome();
}

/* ------------------------------------------- fire-once viewport watcher
   یک IntersectionObserverِ مشترک برای کل صفحه: هر عنصر یک بار — به‌محض
   رسیدن به دید — صدا زده و از observer جدا می‌شود. همهٔ ورودها/شمارنده‌ها از
   همین عبور می‌کنند (به‌جای تریگرِ اسکرولی): هم ارزان‌تر است، هم — برخلاف
   انیمیشنِ وابسته به اسکرول — اگر اسکرول یا درایورِ انیمیشن از کار بیفتد باز
   هم «هرچه در دید است» را گزارش می‌کند، پس هیچ محتوایی روی صفحهٔ خالی جا
   نمی‌ماند. */
const viewCallbacks = new WeakMap();
let viewObserver = null;
function onceIntersecting(el, cb) {
  if (!("IntersectionObserver" in window)) {
    cb();
    return;
  }
  // عناصری که از قبل داخلِ دید یا از آن رد شده‌اند (مثلاً صفحه پيش از
  // راه‌افتادنِ ورودها اسکرول شده) بلافاصله اجرا می‌شوند؛ فقط عناصرِ هنوز
  // پایین‌تر از دید مشاهده می‌شوند. هم «گذشته» را از پنهان‌ماندن نجات
  // می‌دهد، هم اولین صفحه را به frameِ بعدی وابسته نمی‌کند.
  const rect = el.getBoundingClientRect();
  if (rect.top < (window.innerHeight || 800) * 0.88) {
    cb();
    return;
  }
  if (!viewObserver) {
    viewObserver = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          const fn = viewCallbacks.get(entry.target);
          viewObserver.unobserve(entry.target);
          viewCallbacks.delete(entry.target);
          if (fn) fn();
        }
      },
      { rootMargin: "0px 0px -12% 0px" },
    );
  }
  viewCallbacks.set(el, cb);
  viewObserver.observe(el);
}

/* ------------------------------------------------- content safety net
   هر چیزی که با انیمیشن «دیده می‌شود» (ورودِ کارت‌ها، شمارنده‌ها، نوارهای
   پیشرفت) یک تابعِ «مقدارِ نهایی» در این صف ثبت می‌کند و فقط وقتی انیمیشنش
   کامل شد از صف بیرون می‌رود. اگر بنا به هر دلیلی انیمیشن‌ها جلو نروند —
   خطای زمان‌اجرا، تبِ پس‌زمینه، پرینت/اسکرین‌شات، توقفِ رندر یا توقفِ ticker
   — این توابع در زمانِ مشخصی مقدارِ نهایی را مستقیم می‌نویسند تا صفحه هرگز
   بدونِ متن و عدد جا نماند. */
const safetyQueue = new Set();
function onContentTimeout(apply, el = null) {
  const entry = { apply, el };
  safetyQueue.add(entry);
  return entry;
}
function clearSafety(entry) {
  if (entry) safetyQueue.delete(entry);
}
function runContentSafety(scope = "viewport") {
  const vh = window.innerHeight || 800;
  for (const entry of [...safetyQueue]) {
    if (scope !== "all" && entry.el) {
      const r = entry.el.getBoundingClientRect();
      if (r.top > vh) continue; // هنوز پایین‌تر از دید است
    }
    safetyQueue.delete(entry);
    try {
      entry.apply();
    } catch {
      /* تورِ اطمینان هرگز نباید صفحه را خراب کند */
    }
  }
}
window.addEventListener("error", () => runContentSafety("all"));
// پیش از چاپ (که اسکرولی ندارد) هرچه در دید است باید کامل باشد.
window.addEventListener("beforeprint", () => runContentSafety("all"));
setTimeout(() => runContentSafety("viewport"), 2500);
setTimeout(() => runContentSafety("viewport"), 8000);

/* ------------------------------------------------------- shared track drag */

// کشیدنِ ماوس روی یک ترکِ اسکرولِ افقی (اسلایدر نظرات، کاروسل‌ها). لمس از
// اسکرولِ خودِ مرورگر استفاده می‌کند؛ کلیک‌هایی که واقعاً کشیده شده‌اند خنثی
// می‌شوند تا روی کارت‌های قابل‌کلیک اثر نگذارند.
function enableTrackDrag(track) {
  let dragging = false;
  let startX = 0;
  let startSL = 0;
  let moved = 0;
  track.addEventListener("pointerdown", (e) => {
    if (e.pointerType !== "mouse") return;
    // وقتی ترک سرریز ندارد (مثلاً گریدِ دسکتاپ یا کاروسلی که جا شده) کشیدن
    // بی‌معنی است و نباید کلیک‌های کارت را مسدود کند.
    if (track.scrollWidth <= track.clientWidth + 1) return;
    dragging = true;
    moved = 0;
    startX = e.clientX;
    startSL = track.scrollLeft;
    track.classList.add("dragging");
    track.setPointerCapture(e.pointerId);
  });
  track.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    const dx = e.clientX - startX;
    moved = Math.max(moved, Math.abs(dx));
    track.scrollLeft = startSL + dx;
  });
  const endDrag = () => {
    if (!dragging) return;
    dragging = false;
    track.classList.remove("dragging");
  };
  track.addEventListener("pointerup", endDrag);
  track.addEventListener("pointercancel", endDrag);
  track.addEventListener(
    "click",
    (e) => {
      if (moved > 8) {
        e.preventDefault();
        e.stopPropagation();
      }
    },
    true,
  );
}

/* ------------------------------------------------------- testimonial slider */

/* نقطههای کاروسل — دینامیک: پرشدن هر نقطه نشانِ «چسبندگی» کارتِ متناظر
   به مرکزِ قاب است؛ هنگامِ کشیدن، موجِ طلاییِ پرشدن پیوسته از نقطهای
   به نقطهٔ دیگر میرود و نقطهٔ کارتِ مرکزی بزرگتر میشود.
   (چون تبدیلاتِ RTL در شمارشها دامدار است، مرکزها با getBoundingClientRect
   نسبی حساب میشوند و کارتِ مخفی (پهنای صفر) هم بیضرر است.) */
function fillDots(scroller, cards, dots) {
  if (!dots || !dots.length || !cards) return;
  const box = scroller.getBoundingClientRect();
  const w = box.width;
  let best = -1;
  let bestDist = Infinity;
  for (let i = 0; i < cards.length && i < dots.length; i++) {
    const r = cards[i].getBoundingClientRect();
    const dist = Math.abs(r.left - box.left + r.width / 2 - w / 2);
    const fd = Math.max(0, Math.min(1, 1 - dist / Math.max(r.width, 1)));
    dots[i].style.setProperty("--fd", fd.toFixed(3));
    if (dist < bestDist) {
      bestDist = dist;
      best = i;
    }
  }
  dots.forEach((d, i) => d.classList.toggle("active", i === best));
}

function initSliders({ REDUCED, faDigits }) {
  // هر [data-slider] یک نمونهٔ مستقل است؛ دکمه‌ها و نقاط داخل همان
  // data-slider-root جستجو می‌شوند تا چند اسلایدر در یک صفحه کار کنند.
  document.querySelectorAll("[data-slider]").forEach((slider) => {
    const root = slider.closest("[data-slider-root]");
    const cards = [...slider.querySelectorAll(".t-card")];
    const dotsWrap = root && root.querySelector("[data-slider-dots]");
    if (!cards.length || !dotsWrap) return;
    const dots = cards.map((_, i) => {
      const d = document.createElement("button");
      d.className = "slider-dot" + (i === 0 ? " active" : "");
      d.setAttribute("aria-label", "نظر " + faDigits(i + 1));
      d.addEventListener("click", () => {
        const target = -cards[i].offsetLeft + 24;
        slider.scrollTo({ left: target, behavior: REDUCED ? "auto" : "smooth" });
      });
      dotsWrap.appendChild(d);
      return d;
    });

    const maxScroll = () => slider.scrollWidth - slider.clientWidth;
    const progress = () =>
      maxScroll() > 0
        ? Math.min(1, Math.abs(slider.scrollLeft) / maxScroll())
        : 0;
    let ticking = false;
    slider.addEventListener(
      "scroll",
      () => {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(() => {
          fillDots(slider, cards, dots);
          ticking = false;
        });
      },
      { passive: true },
    );
    fillDots(slider, cards, dots);

    const step = () => cards[0].offsetWidth + 24;
    const next = () => {
      if (progress() > 0.92)
        slider.scrollTo({ left: 0, behavior: REDUCED ? "auto" : "smooth" });
      else
        slider.scrollBy({ left: -step(), behavior: REDUCED ? "auto" : "smooth" });
    };
    const prev = () =>
      slider.scrollBy({ left: step(), behavior: REDUCED ? "auto" : "smooth" });
    const nextBtn = root && root.querySelector("[data-slider-next]");
    const prevBtn = root && root.querySelector("[data-slider-prev]");
    if (nextBtn) nextBtn.addEventListener("click", next);
    if (prevBtn) prevBtn.addEventListener("click", prev);

  // Autoplay
  if (!REDUCED) {
    let hovered = false;
    const loop = () => {
      setTimeout(() => {
        if (!hovered && !document.hidden) next();
        loop();
      }, 5600);
    };
    loop();
    slider.addEventListener("pointerenter", () => (hovered = true));
    slider.addEventListener("pointerleave", () => (hovered = false));
  }

  // Mouse drag
  enableTrackDrag(slider);
  });
}

/* ------------------------------------------------------------- carousels */

// هر [data-carousel] یک نمونهٔ مستقل است: کاروسل روی هم‌رفتهٔ CSS scroll-snap
// است و دکمه‌ها/نقاط/کیبورد فقط به همان نمونه مربوط می‌شوند. جهت RTL است:
// دکمهٔ بعدی سمت چپ می‌نشیند و ArrowLeft به جلو می‌رود.
function initCarousels({ REDUCED, faDigits }) {
  document.querySelectorAll("[data-carousel]").forEach((root) => {
    const track = root.querySelector("[data-carousel-track]");
    if (!track) return;
    const dotsWrap = root.querySelector("[data-carousel-dots]");
    const prevBtn = root.querySelector("[data-carousel-prev]");
    const nextBtn = root.querySelector("[data-carousel-next]");
    const controlsWrap = root.querySelector("[data-carousel-controls]");
    const GAP = 24;

    // اسلایدها می‌توانند در طول زمان مخفی شوند (فیلتر نمونه‌کارها با is-hidden
    // کارت‌ها را حذف می‌کند)، بنابراین نقاط و گامِ اسکرول باید هر بار از روی
    // اسلایدهای مرئیِ همان لحظه محاسبه شوند.
    const visible = () =>
      [...track.children].filter((s) => !s.classList.contains("is-hidden"));

    let dots = null;
    const buildDots = (slides) => {
      if (!dotsWrap) return;
      dotsWrap.innerHTML = "";
      dots = slides.map((slide, i) => {
        const d = document.createElement("button");
        d.type = "button";
        d.className = "slider-dot" + (i === 0 ? " active" : "");
        d.setAttribute("aria-label", "اسلاید " + faDigits(i + 1));
        d.addEventListener("click", () => {
          track.scrollTo({
            left: -slide.offsetLeft + GAP,
            behavior: REDUCED ? "auto" : "smooth",
          });
        });
        dotsWrap.appendChild(d);
        return d;
      });
    };

    // فیلتر عوض شده: اسکرول به ابتدا، بازسازی نقاط و مخفی کردن کنترل‌ها وقتی
    // هیچ اسلاید مرئی‌ای نمانده است.
    const refresh = () => {
      const slides = visible();
      track.scrollTo({ left: 0, behavior: "auto" });
      buildDots(slides);
      if (dots && dots.length) fillDots(track, slides, dots);
      if (controlsWrap)
        controlsWrap.classList.toggle("hidden", slides.length === 0);
    };

    buildDots(visible());
    if (dots && dots.length) fillDots(track, visible(), dots);
    root.addEventListener("pf:changed", refresh);

    const maxScroll = () => track.scrollWidth - track.clientWidth;
    const progress = () =>
      maxScroll() > 0
        ? Math.min(1, Math.abs(track.scrollLeft) / maxScroll())
        : 0;
    let ticking = false;
    track.addEventListener(
      "scroll",
      () => {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(() => {
          if (dots && dots.length) fillDots(track, visible(), dots);
          ticking = false;
        });
      },
      { passive: true },
    );

    const step = () => {
      const slides = visible();
      return slides.length ? slides[0].offsetWidth + GAP : 0;
    };
    const next = () => {
      if (progress() > 0.92)
        track.scrollTo({ left: 0, behavior: REDUCED ? "auto" : "smooth" });
      else
        track.scrollBy({ left: -step(), behavior: REDUCED ? "auto" : "smooth" });
    };
    const prev = () =>
      track.scrollBy({ left: step(), behavior: REDUCED ? "auto" : "smooth" });
    if (nextBtn) nextBtn.addEventListener("click", next);
    if (prevBtn) prevBtn.addEventListener("click", prev);

    // کیبورد: ترک focusable است. ArrowLeft در RTL به جلو (سمت چپ) می‌رود.
    track.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") {
        e.preventDefault();
        next();
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        prev();
      } else if (e.key === "Home") {
        e.preventDefault();
        track.scrollTo({ left: 0, behavior: "auto" });
      } else if (e.key === "End") {
        e.preventDefault();
        track.scrollTo({ left: -maxScroll(), behavior: "auto" });
      }
    });

    enableTrackDrag(track);
  });
}

/* ------------------------------------------------------- portfolio filter */

function initPortfolioFilter({ REDUCED, faDigits }) {
  // هر نمونه از فیلتر در یک wrapper با data-pf-root قرار دارد تا چند فیلتر
  // روی یک صفحه (مثلاً خانه + آرشیو) بدون تداخل کار کنند.
  document.querySelectorAll("[data-pf-root]").forEach((root) => {
    const pfGrid = root.querySelector("[data-pf-grid]");
    const pfFilters = root.querySelector("[data-pf-filters]");
    const pfCount = root.querySelector("[data-pf-count]");
    const pfEmpty = root.querySelector("[data-pf-empty]");
    if (!pfGrid || !pfFilters) return;

    const items = [...pfGrid.querySelectorAll(".pf-item")];
    // فقط صفحهٔ آرشیو آدرس را با فیلتر همگام می‌کند (data-pf-sync).
    const syncUrl = root.hasAttribute("data-pf-sync");

    // وقتی کارت‌ها پنهان/ظاهر می‌شوند، کاروسل باید نقاطش را بازسازی کند و
    // اسکرول را به ابتدا برگرداند (data-carousel روی همین section listen می‌کند).
    const announce = () =>
      pfGrid.dispatchEvent(new CustomEvent("pf:changed", { bubbles: true }));

  const apply = (cat, skipUrl) => {
    let shown = 0;
    items.forEach((el) => {
      const match = cat === "all" || el.dataset.cat === cat;
      if (match) shown++;
      // ورودِ کارت با keyframesِ CSS (rvTileIn) و پلکانِ --pf-i انجام
      // می‌شود؛ پنهان‌کردن هم فقط یک کلاس است. پس هیچ انیمیشنِ JS ای
      // در فیلتر نیست.
      if (match) {
        el.classList.remove("is-hidden");
        // کارتی که با فیلتر برمی‌گردد باید بلافاصله «رسیده» باشد، وگرنه
        // پشتِ حالتِ پنهانِ ورودِ اولیه می‌ماند؛ حرکتِ ورود را همان
        // keyframesِ pf-in می‌سازد.
        el.classList.add("is-in");
        el.style.setProperty("--pf-i", String(Math.min(shown, 10)));
        el.classList.remove("pf-in");
        void el.offsetWidth;
        el.classList.add("pf-in");
      } else {
        el.classList.add("is-hidden");
      }
    });
    announce();
    if (pfCount) pfCount.textContent = `${faDigits(shown)} PROJECTS`;
    if (pfEmpty) pfEmpty.classList.toggle("hidden", shown > 0);
    if (syncUrl && !skipUrl) {
      const url =
        cat === "all" ? location.pathname : `${location.pathname}?category=${cat}`;
      history.replaceState(null, "", url);
    }
  };

  const setActive = (btn) => {
    pfFilters.querySelectorAll(".flt-btn").forEach((b) =>
      b.classList.toggle("active", b === btn),
    );
  };

  pfFilters.addEventListener("click", (e) => {
    const btn = e.target.closest(".flt-btn");
    if (!btn) return;
    setActive(btn);
    apply(btn.dataset.filter);
  });

  // بازدید از ?category=<slug> همان دسته را از ابتدا فعال می‌کند.
  const initial = new URLSearchParams(location.search).get("category");
  if (initial) {
    const btn = pfFilters.querySelector(`[data-filter="${initial}"]`);
    if (btn) {
      setActive(btn);
      apply(initial, true);
    }
  }
  });
}

/* ------------------------------------------------------- marquee duplication */

function initMarquees() {
  // Each group must be at least as wide as its container, otherwise the loop
  // point shows a gap; duplicate the content once to guarantee the width.
  // The copies are decorative — hide them from the accessibility tree.
  document
    .querySelectorAll("#tech .marquee-group, #trusted .marquee-group")
    .forEach((g) => {
      g.append(
        ...[...g.children].map((c) => {
          const clone = c.cloneNode(true);
          clone.setAttribute("aria-hidden", "true");
          return clone;
        }),
      );
    });
}

/* ------------------------------------------------------- stat counts (data-count) */

function initStatCounts() {
  document.querySelectorAll("[data-count]").forEach((el) => {
    const target = parseFloat(el.dataset.count);
    const prefix = el.dataset.prefix || "";
    const suffix = el.dataset.suffix || "";
    const settle = () => {
      el.textContent = prefix + faDigits(target) + suffix;
    };
    if (REDUCED) {
      settle();
      return;
    }
    onContentTimeout(settle, el);
    onceIntersecting(el, () =>
      tweenNumbers(
        2000,
        (v) => {
          el.textContent = prefix + faDigits(Math.round(v)) + suffix;
        },
        { to: target, ease: easeOutExpo },
      ),
    );
  });
}

/* ------------------------------------------------------- service build bars */

function initBuildBars() {
  document.querySelectorAll(".svc-build-bar").forEach((bar) => {
    const pct = bar.closest(".svc-card")?.querySelector("[data-build-pct]");
    const settle = () => {
      bar.style.width = "100%";
      if (pct) pct.textContent = "۱۰۰٪";
    };
    if (REDUCED) {
      settle();
      return;
    }
    onContentTimeout(settle, bar);
    onceIntersecting(bar, () => {
      // خودِ پهنای نوار با ترنزیشنِ CSS کشیده می‌شود؛ JS فقط عدد را
      // می‌شمارد (CSS نمی‌تواند ارقامِ فارسی را فرمت کند).
      bar.style.width = "100%";
      if (!pct) return;
      tweenNumbers(
        1800,
        (v) => {
          pct.textContent = faDigits(Math.round(v)) + "٪";
        },
        { to: 100, ease: easeOutExpo },
      );
    });
  });
}

/* ------------------------------------------------------- process GPS draw */

function initGpsDraw({ REDUCED }) {
  const gpsDraws = [...document.querySelectorAll(".gps-draw")];
  if (!gpsDraws.length || REDUCED) return;

  // کشیده‌شدنِ مسیر با اسکرول و حرکتِ نقطه روی همان مسیر، هر دو انیمیشنِ
  // CSS هستند (motion.css + animation-timeline: view()). این تابع فقط
  // هندسهٔ هر مسیر را به نقطهٔ متناظرش می‌دهد تا مرورگر خودش نقطه را روی
  // مسیر بلغزاند؛ هیچ فریم‌به‌فریمی از JS هزینه نمی‌شود.
  const supported = (() => {
    try {
      return (
        CSS.supports("offset-path", 'path("M0 0 L1 1")') &&
        CSS.supports("animation-timeline", "view()")
      );
    } catch {
      return false;
    }
  })();
  if (!supported) return;

  // هر مسیر مالِ نزدیک‌ترین [data-gps-root] است (صفحهٔ خانه و صفحهٔ خدمت هر
  // کدام یک نمونه دارند).
  const roots = [
    ...new Set(gpsDraws.map((p) => p.closest("[data-gps-root]")).filter(Boolean)),
  ];
  roots.forEach((root) => {
    const paths = [...root.querySelectorAll(".gps-draw")];
    const dots = [...root.querySelectorAll(".gps-dot")];
    paths.forEach((path, i) => {
      const dot = dots[i];
      const d = path.getAttribute("d");
      if (!dot || !d) return;
      dot.style.offsetPath = `path("${d}")`;
      dot.style.offsetRotate = "0deg";
      // مختصاتِ اصلی خنثی می‌شود تا نقطه دو بار جابه‌جا نشود (offset-path
      // خودش مکان را تعیین می‌کند).
      dot.setAttribute("cx", "0");
      dot.setAttribute("cy", "0");
    });
  });
}

/* ------------------------------------------------- free-text stat counters
   ``data-count-text``: برای اعدادی که متنِ آزاد هستند (مثل «۹۸/۱۰۰» یا
   «زیر ۲ ثانیه»). اولین رشتهٔ رقم (فارسی یا لاتین) شمارش می‌شود و بقیهٔ
   متن دورش ثابت می‌ماند. عنصر بدونِ JS هم مقدارِ واقعی را از سرور می‌گیرد. */

function initStatCountText() {
  const toLatin = (str) =>
    str.replace(/[۰-۹]/g, (d) => String("۰۱۲۳۴۵۶۷۸۹".indexOf(d)));
  document.querySelectorAll("[data-count-text]").forEach((el) => {
    const match = el.dataset.countText.match(/^([^\d۰-۹]*)([\d۰-۹][\d۰-۹,،]*)(.*)$/);
    if (!match) return;
    const [, head, digits, tail] = match;
    const target = Number(toLatin(digits).replace(/[,،]/g, ""));
    if (!Number.isFinite(target)) return;
    const render = (v) => {
      el.textContent = head + faDigits(Math.round(v)) + tail;
    };
    if (REDUCED) {
      render(target);
      return;
    }
    onContentTimeout(() => render(target), el);
    onceIntersecting(el, () =>
      tweenNumbers(2000, (v) => render(v), { to: target, ease: easeOutExpo }),
    );
  });
}

/* ------------------------------------------------------- FAQ accordion */

function initFaq() {
  document.querySelectorAll(".faq-item").forEach((item) => {
    const q = item.querySelector(".faq-q");
    const a = item.querySelector(".faq-a");
    if (!q || !a) return;
    q.addEventListener("click", () => {
      const isOpen = item.classList.contains("open");
      // Close the others
      document.querySelectorAll(".faq-item.open").forEach((other) => {
        if (other === item) return;
        other.classList.remove("open");
        other.querySelector(".faq-q").setAttribute("aria-expanded", "false");
        other.querySelector(".faq-a").style.maxHeight = "0";
      });
      item.classList.toggle("open", !isOpen);
      q.setAttribute("aria-expanded", String(!isOpen));
      a.style.maxHeight = isOpen ? "0" : a.scrollHeight + "px";
    });
  });
}

/* ------------------------------------------ blog article: TOC + progress + copy */

// صفحهٔ مقالهٔ بلاگ: نوار پیشرفتِ خواندن، لینکِ فعالِ فهرست مطالب و دکمهٔ
// کپیِ لینک. همه‌چیز با data-* قلاب می‌شود تا هیچ آی‌دیِ ثابتی روی صفحه نباشد
// و این کد فقط روی صفحات مقاله کار کند.
function initArticleChrome() {
  // نوار پیشرفتِ خواندن — نسبتِ اسکرولِ شده از متن مقاله را پر می‌کند.
  const body = document.querySelector("[data-reading-progress]");
  const bar = document.querySelector("[data-reading-bar]");
  if (body && bar) {
    const sync = () => {
      const r = body.getBoundingClientRect();
      const total = r.height;
      const passed = Math.min(Math.max(-r.top, 0), total);
      bar.style.transform = `scaleX(${total > 0 ? passed / total : 0})`;
    };
    window.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", sync);
    sync();
  }

  // فهرست مطالب — لینکِ متناظر با هدینگی که در دید است فعال می‌شود.
  const toc = document.querySelector("[data-toc]");
  if (toc) {
    const links = [...toc.querySelectorAll("[data-toc-link]")];
    const headings = links
      .map((a) => {
        try {
          return document.querySelector(
            `#${CSS.escape(a.getAttribute("href").slice(1))}`,
          );
        } catch {
          return null;
        }
      })
      .filter(Boolean);
    if (headings.length) {
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            links.forEach((a) =>
              a.classList.toggle("active", a.hash === `#${entry.target.id}`),
            );
          });
        },
        { rootMargin: "-20% 0px -70% 0px" },
      );
      headings.forEach((h) => io.observe(h));
    }
  }

  // دکمهٔ کپیِ لینک — حالتِ «کپی شد» دو ثانیه می‌ماند.
  document.querySelectorAll("[data-copy-link]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const def = btn.querySelector("[data-copy-default]");
      const done = btn.querySelector("[data-copy-done]");
      const flashDone = () => {
        if (def) def.hidden = true;
        if (done) done.hidden = false;
        setTimeout(() => {
          if (done) done.hidden = true;
          if (def) def.hidden = false;
        }, 2000);
      };
      if (navigator.clipboard) {
        navigator.clipboard
          .writeText(location.href)
          .then(flashDone)
          .catch(() => showToast("کپی کردن لینک ناموفق بود"));
      } else {
        showToast("مرورگر اجازهٔ کپی نمی‌دهد");
      }
    });
  });
}

/* ------------------------------------------------------- HTMX + toast bridge */

// After an HTMX swap, if the new content carries a [data-toast] element,
// announce its message (used by the contact form success state).
const announceToast = () => {
  const el = document.querySelector("[data-toast]");
  if (el) showToast(el.dataset.toast);
};
document.addEventListener("htmx:afterSettle", announceToast);

/* ------------------------------------------------------- boot */

// راه‌اندازی با محافظ: اگر هر بخشی خطا داد، کلاسِ motion از <html> برداشته
// می‌شود تا محتوا هرگز پشتِ حالتِ پنهانِ انیمیشن‌ها جا نماند (درسِ صفحهٔ خالی).
const boot = () => {
  try {
    init();
  } catch (e) {
    document.documentElement.classList.remove("motion");
    console.error("[pixoria]", e);
  }
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}
