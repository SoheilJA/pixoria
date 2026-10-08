/**
 * Pixoria — shared interaction layer (v2 design).
 *
 * Ported from the inline script of new/index.html. Handles smooth scroll,
 * scroll-driven reveals/counters, magnetic + tilt effects, the mobile menu,
 * scroll progress, the testimonial slider, the media (video/audio) cards,
 * the portfolio filter, marquee duplication, the process GPS draw, the FAQ
 * accordion, the toast and the blog article chrome (reading-progress bar,
 * table-of-contents highlight, copy-link button).
 *
 * Loaded as an ES module from base.html. GSAP + ScrollTrigger are expected as
 * globals (defer classic scripts); every feature degrades gracefully when they
 * are missing, when the user prefers reduced motion, or on touch input.
 * Lenis is imported as a module so no global is required.
 */

import Lenis from "./vendor/lenis.mjs";

const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
const TOUCH = matchMedia("(hover: none)").matches;

const FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹";
const faDigits = (value) => String(value).replace(/\d/g, (d) => FA_DIGITS[d]);
const fmtTime = (seconds) =>
  faDigits(Math.floor(seconds / 60)) +
  ":" +
  faDigits(String(Math.floor(seconds % 60)).padStart(2, "0"));

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
  const gsap = window.gsap;
  const ScrollTrigger = window.ScrollTrigger;
  const hasGsap = typeof gsap !== "undefined";
  if (hasGsap && ScrollTrigger) gsap.registerPlugin(ScrollTrigger);

  /* ---------------- smooth scroll (Lenis) ---------------- */
  let lenis = null;
  if (!REDUCED && hasGsap) {
    lenis = new Lenis({ duration: 1.1, smoothWheel: true });
    lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  } else {
    document.documentElement.style.scrollBehavior = "smooth";
  }

  /* ---------------- mobile menu ---------------- */
  const menu = document.getElementById("mobile-menu");
  const menuOpenBtn = document.getElementById("menu-open");
  const bodyLock = (on) => {
    document.body.style.overflow = on ? "hidden" : "";
    if (lenis) on ? lenis.stop() : lenis.start();
  };
  const closeMenu = () => {
    if (!menu || !menu.classList.contains("open")) return;
    menu.classList.remove("open");
    if (menuOpenBtn) menuOpenBtn.setAttribute("aria-expanded", "false");
    bodyLock(false);
  };
  if (menu && menuOpenBtn) {
    const openMenu = () => {
      menu.classList.add("open");
      menuOpenBtn.setAttribute("aria-expanded", "true");
      bodyLock(true);
    };
    menuOpenBtn.addEventListener("click", openMenu);
    menu.querySelectorAll("[data-menu-close]").forEach((b) =>
      b.addEventListener("click", closeMenu),
    );
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeMenu();
    });
  }

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
          closeMenu();
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

  /* ---------------- reveal animations ---------------- */
  // کارت‌هایی که بعد از یک تعویضِ HTMX (مثلاً «مقالات بیشتر») وارد صفحه
  // می‌شوند را با data-blog-reveal علامت‌گذاری می‌کنیم؛ آن‌ها در زمانِ boot
  // هنوز وجود ندارند و باید پس از settle دوباره راه‌اندازی شوند.
  const revealEl = (el) => {
    const type = el.dataset.reveal || "up";
    const vars = {
      opacity: 0,
      duration: 1,
      ease: "power3.out",
      delay: parseFloat(el.dataset.delay || 0),
    };
    if (type === "up") vars.y = 50;
    else if (type === "right") vars.x = 60;
    else if (type === "left") vars.x = -60;
    else if (type === "scale") vars.scale = 0.92;
    gsap.from(el, {
      ...vars,
      scrollTrigger: { trigger: el, start: "top 88%", once: true },
    });
  };
  if (hasGsap && !REDUCED) {
    gsap.utils.toArray("[data-reveal]").forEach(revealEl);
  }
  // تعویضِ HTMX → فقط عناصرِ تازه‌اضافه‌شده آنیمیشن می‌گیرند (با رعایت
  // prefers-reduced-motion).
  document.addEventListener("htmx:afterSettle", () => {
    if (!hasGsap || REDUCED) return;
    document.querySelectorAll("[data-blog-reveal]").forEach((el) => {
      if (el.dataset.revealDone) return;
      el.dataset.revealDone = "1";
      revealEl(el);
      if (!TOUCH) tiltCard(el);
    });
  });

  /* ---------------- counters (data-counter) ---------------- */
  document.querySelectorAll("[data-counter]").forEach((el) => {
    const target = +el.dataset.counter;
    const fmt = (v) =>
      (el.dataset.prefix || "") +
      v.toLocaleString("fa-IR") +
      (el.dataset.suffix || "");
    if (!hasGsap || REDUCED) {
      el.textContent = fmt(target);
      return;
    }
    const o = { v: 0 };
    el.textContent = fmt(0);
    gsap.to(o, {
      v: target,
      duration: 1.8,
      ease: "power2.out",
      onUpdate: () => {
        el.textContent = fmt(Math.round(o.v));
      },
      scrollTrigger: { trigger: el, start: "top 92%", once: true },
    });
  });

  /* ---------------- magnetic buttons ---------------- */
  if (hasGsap && !TOUCH && !REDUCED) {
    document.querySelectorAll("[data-magnetic]").forEach((btn) => {
      const xTo = gsap.quickTo(btn, "x", { duration: 0.4, ease: "power3" });
      const yTo = gsap.quickTo(btn, "y", { duration: 0.4, ease: "power3" });
      btn.addEventListener("mousemove", (e) => {
        const r = btn.getBoundingClientRect();
        xTo((e.clientX - r.left - r.width / 2) * 0.3);
        yTo((e.clientY - r.top - r.height / 2) * 0.35);
      });
      btn.addEventListener("mouseleave", () => {
        xTo(0);
        yTo(0);
      });
    });
  }

  /* ---------------- 3D tilt cards + glare ---------------- */
  // کارت‌های تعویض‌شده با HTMX (data-blog-reveal) هم tilt می‌گیرند.
  const tiltCard = (card) => {
    gsap.set(card, { transformPerspective: 900 });
    const rx = gsap.quickTo(card, "rotationX", { duration: 0.5, ease: "power2" });
    const ry = gsap.quickTo(card, "rotationY", { duration: 0.5, ease: "power2" });
    card.addEventListener("mousemove", (e) => {
      const r = card.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width;
      const py = (e.clientY - r.top) / r.height;
      rx((py - 0.5) * -6);
      ry((px - 0.5) * 6);
      card.style.setProperty("--gx", px * 100 + "%");
      card.style.setProperty("--gy", py * 100 + "%");
    });
    card.addEventListener("mouseleave", () => {
      rx(0);
      ry(0);
    });
  };
  if (hasGsap && !TOUCH && !REDUCED) {
    document.querySelectorAll("[data-tilt]").forEach(tiltCard);
  }

  /* ---------------- floating elements ---------------- */
  if (hasGsap && !REDUCED) {
    document.querySelectorAll("[data-float]").forEach((el) => {
      const amp = parseFloat(el.dataset.float || "10");
      gsap.to(el, {
        y: gsap.utils.random(-amp, amp),
        duration: gsap.utils.random(2.6, 4.6),
        yoyo: true,
        repeat: -1,
        ease: "sine.inOut",
        delay: gsap.utils.random(0, 1.4),
      });
    });
    // Rotating floaters (planets and debris)
    document.querySelectorAll("[data-float-spin]").forEach((el) => {
      const amp = parseFloat(el.dataset.floatSpin || "14");
      const dir = gsap.utils.random(-1, 1) < 0 ? -1 : 1;
      gsap.to(el, {
        y: gsap.utils.random(-amp, amp),
        rotation: dir * gsap.utils.random(4, 12),
        duration: gsap.utils.random(3, 5),
        yoyo: true,
        repeat: -1,
        ease: "sine.inOut",
        delay: gsap.utils.random(0, 1.2),
      });
    });
  }

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

  initSliders({ hasGsap, REDUCED, faDigits });
  initCarousels({ REDUCED, faDigits });
  initMediaCards({ hasGsap, REDUCED, fmtTime });
  initPortfolioFilter({ hasGsap, REDUCED, faDigits });
  initMarquees();
  initStatCounts({ hasGsap, ScrollTrigger });
  initBuildBars({ hasGsap, ScrollTrigger });
  initGpsDraw({ hasGsap, ScrollTrigger, REDUCED });
  initFaq();
  initArticleChrome();

  window.addEventListener("load", () => {
    if (hasGsap && ScrollTrigger) ScrollTrigger.refresh();
  });
}

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

function initSliders({ hasGsap, REDUCED, faDigits }) {
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
          const idx = Math.round(progress() * (cards.length - 1));
          dots.forEach((d, i) => d.classList.toggle("active", i === idx));
          ticking = false;
        });
      },
      { passive: true },
    );

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
      if (controlsWrap)
        controlsWrap.classList.toggle("hidden", slides.length === 0);
    };

    buildDots(visible());
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
          const n = visible().length;
          if (n) {
            const idx = Math.round(progress() * (n - 1));
            if (dots)
              dots.forEach((d, i) => d.classList.toggle("active", i === idx));
          }
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

/* ------------------------------------------------------- shared media simulator */

function mediaSim({ dur, onTick, onEnd }) {
  let t = 0;
  let raf = null;
  let last = 0;
  const loop = (now) => {
    if (!raf) return;
    const dt = (now - last) / 1000;
    last = now;
    t = Math.min(dur, t + dt);
    onTick(t);
    if (t >= dur) {
      raf = null;
      onEnd && onEnd();
      return;
    }
    raf = requestAnimationFrame(loop);
  };
  return {
    play() {
      if (raf) return;
      last = performance.now();
      raf = requestAnimationFrame(loop);
    },
    pause() {
      if (raf) {
        cancelAnimationFrame(raf);
        raf = null;
      }
    },
    reset() {
      this.pause();
      t = 0;
      onTick(0);
    },
  };
}

function initMediaCards({ hasGsap, REDUCED, fmtTime }) {
  const gsap = window.gsap;

  /* ---------------- video cards (simulated playback) ---------------- */
  document.querySelectorAll("[data-video-card]").forEach((card) => {
    const vPlay = card.querySelector("[data-v-play]");
    if (!vPlay) return;
    const vImg = card.querySelector("[data-v-img]");
    const vScrim = card.querySelector("[data-v-scrim]");
    const vProg = card.querySelector("[data-v-prog]");
    const vTime = card.querySelector("[data-v-time]");
    const DUR = Math.max(1, parseInt(card.dataset.videoCard || "48", 10) || 48);
    let kb = null;
    const sim = mediaSim({
      dur: DUR,
      onTick: (t) => {
        if (vProg) vProg.style.width = (t / DUR) * 100 + "%";
        if (vTime) vTime.textContent = fmtTime(t) + " / " + fmtTime(DUR);
      },
      onEnd: () => {
        vPlay.classList.remove("is-playing");
        if (vScrim) vScrim.style.opacity = "";
        if (kb && hasGsap) {
          kb.kill();
          gsap.set(vImg, { scale: 1 });
        }
        sim.reset();
      },
    });
    vPlay.addEventListener("click", () => {
      const on = vPlay.classList.toggle("is-playing");
      if (on) {
        if (vScrim) vScrim.style.opacity = "0";
        sim.play();
        if (hasGsap && !REDUCED)
          kb = gsap.to(vImg, {
            scale: 1.12,
            duration: 9,
            yoyo: true,
            repeat: -1,
            ease: "sine.inOut",
          });
      } else {
        sim.pause();
        if (vScrim) vScrim.style.opacity = "";
        if (kb && hasGsap) {
          kb.kill();
          gsap.set(vImg, { scale: 1 });
        }
      }
    });
  });

  /* ---------------- audio cards (real WebAudio playback) ---------------- */
  document.querySelectorAll("[data-audio-card]").forEach((card) => {
    const aPlay = card.querySelector("[data-a-play]");
    const barsWrap = card.querySelector("[data-a-bars]");
    const aCur = card.querySelector("[data-a-cur]");
    if (!aPlay || !barsWrap) return;
    const DUR = Math.max(1, parseInt(card.dataset.audioCard || "65", 10) || 65);
    const N = 44;
    const bars = [];
    for (let i = 0; i < N; i++) {
      const b = document.createElement("span");
      b.className = "w-bar";
      b.style.height = 18 + Math.random() * 82 + "%";
      b.style.animationDelay = (Math.random() * 1.2).toFixed(2) + "s";
      barsWrap.appendChild(b);
      bars.push(b);
    }
    let ctx = null;
    let nodes = null;
    const startSound = () => {
      try {
        const AC = window.AudioContext || window.webkitAudioContext;
        ctx = ctx || new AC();
        if (ctx.state === "suspended") ctx.resume();
        const g = ctx.createGain();
        g.gain.value = 0.0001;
        g.gain.exponentialRampToValueAtTime(0.05, ctx.currentTime + 1);
        const f = ctx.createBiquadFilter();
        f.type = "lowpass";
        f.frequency.value = 520;
        const o1 = ctx.createOscillator();
        o1.type = "sine";
        o1.frequency.value = 112;
        const o2 = ctx.createOscillator();
        o2.type = "sine";
        o2.frequency.value = 168.5;
        const lfo = ctx.createOscillator();
        lfo.frequency.value = 0.25;
        const lg = ctx.createGain();
        lg.gain.value = 0.02;
        lfo.connect(lg);
        lg.connect(g.gain);
        o1.connect(f);
        o2.connect(f);
        f.connect(g);
        g.connect(ctx.destination);
        o1.start();
        o2.start();
        lfo.start();
        nodes = { o1, o2, lfo, g };
      } catch {
        /* no audio — the progress timeline still runs */
      }
    };
    const stopSound = () => {
      if (!nodes) return;
      try {
        nodes.g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.4);
        const n = nodes;
        setTimeout(() => {
          try {
            n.o1.stop();
            n.o2.stop();
            n.lfo.stop();
          } catch {
            /* already stopped */
          }
        }, 500);
      } catch {
        /* already stopped */
      }
      nodes = null;
    };
    const sim = mediaSim({
      dur: DUR,
      onTick: (t) => {
        if (aCur) aCur.textContent = fmtTime(t);
        const p = t / DUR;
        bars.forEach((b, i) =>
          b.classList.toggle("played", (i + 1) / N <= p),
        );
      },
      onEnd: () => {
        aPlay.classList.remove("is-playing");
        barsWrap.classList.remove("playing");
        stopSound();
        sim.reset();
      },
    });
    aPlay.addEventListener("click", () => {
      const on = aPlay.classList.toggle("is-playing");
      if (on) {
        sim.play();
        barsWrap.classList.add("playing");
        startSound();
      } else {
        sim.pause();
        barsWrap.classList.remove("playing");
        stopSound();
      }
    });
  });
}

/* ------------------------------------------------------- portfolio filter */

function initPortfolioFilter({ hasGsap, REDUCED, faDigits }) {
  const gsap = window.gsap;
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
      if (hasGsap && !REDUCED) {
        if (match) {
          el.classList.remove("is-hidden");
          gsap.fromTo(
            el,
            { opacity: 0, scale: 0.92, y: 14 },
            {
              opacity: 1,
              scale: 1,
              y: 0,
              duration: 0.55,
              ease: "power3.out",
              delay: shown * 0.05,
            },
          );
        } else {
          gsap.to(el, {
            opacity: 0,
            scale: 0.92,
            duration: 0.3,
            ease: "power2.in",
            onComplete: () => {
              el.classList.add("is-hidden");
              announce();
            },
          });
        }
      } else {
        el.classList.toggle("is-hidden", !match);
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

function initStatCounts({ hasGsap, ScrollTrigger }) {
  const gsap = window.gsap;
  document.querySelectorAll("[data-count]").forEach((el) => {
    const target = parseFloat(el.dataset.count);
    const prefix = el.dataset.prefix || "";
    const suffix = el.dataset.suffix || "";
    if (hasGsap && ScrollTrigger) {
      const obj = { v: 0 };
      ScrollTrigger.create({
        trigger: el,
        start: "top 85%",
        once: true,
        onEnter: () =>
          gsap.to(obj, {
            v: target,
            duration: 2,
            ease: "power2.out",
            onUpdate: () => {
              el.textContent = prefix + faDigits(Math.round(obj.v)) + suffix;
            },
          }),
      });
    } else {
      el.textContent = prefix + faDigits(target) + suffix;
    }
  });
}

/* ------------------------------------------------------- service build bars */

function initBuildBars({ hasGsap, ScrollTrigger }) {
  const gsap = window.gsap;
  document.querySelectorAll(".svc-build-bar").forEach((bar) => {
    const pct = bar.closest(".svc-card")?.querySelector("[data-build-pct]");
    if (hasGsap && ScrollTrigger) {
      ScrollTrigger.create({
        trigger: bar,
        start: "top 80%",
        once: true,
        onEnter: () => {
          bar.style.width = "100%";
          if (pct) {
            const obj = { v: 0 };
            gsap.to(obj, {
              v: 100,
              duration: 1.8,
              ease: "power2.out",
              onUpdate: () => (pct.textContent = faDigits(Math.round(obj.v)) + "٪"),
            });
          }
        },
      });
    } else {
      bar.style.width = "100%";
      if (pct) pct.textContent = "۱۰۰٪";
    }
  });
}

/* ------------------------------------------------------- process GPS draw */

function initGpsDraw({ hasGsap, ScrollTrigger, REDUCED }) {
  const gsap = window.gsap;
  const gpsDraws = [...document.querySelectorAll(".gps-draw")];
  if (!gpsDraws.length) return;

  const paths = gpsDraws.map((p) => {
    p.style.strokeDasharray = "1";
    p.style.strokeDashoffset = REDUCED ? "0" : "1";
    return { p, len: p.getTotalLength() };
  });
  const dots = [...document.querySelectorAll(".gps-dot")];
  if (hasGsap && ScrollTrigger && !REDUCED) {
    const o = { v: 0 };
    gsap.to(o, {
      v: 1,
      ease: "none",
      scrollTrigger: {
        trigger: "#process",
        start: "top 65%",
        end: "bottom 75%",
        scrub: 0.6,
      },
      onUpdate: () => {
        paths.forEach(({ p, len }, i) => {
          p.style.strokeDashoffset = String(1 - o.v);
          const pt = p.getPointAtLength(len * o.v);
          const dot = dots[i];
          if (dot) {
            dot.setAttribute("cx", pt.x.toFixed(1));
            dot.setAttribute("cy", pt.y.toFixed(1));
          }
        });
      },
    });
  }
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

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
