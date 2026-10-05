/**
 * Pixoria — shared interaction layer (v2 design).
 *
 * Ported from the inline script of new/index.html. Handles smooth scroll,
 * scroll-driven reveals/counters, magnetic + tilt effects, the mobile menu,
 * scroll progress, the testimonial slider, the media (video/audio) cards,
 * the portfolio filter, marquee duplication, the process GPS draw, the FAQ
 * accordion and the toast.
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
// Exposed so templates/HTMX flows (lead form, contact form) can fire it.
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
  if (hasGsap && !REDUCED) {
    gsap.utils.toArray("[data-reveal]").forEach((el) => {
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
    });
  }

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
  if (hasGsap && !TOUCH && !REDUCED) {
    document.querySelectorAll("[data-tilt]").forEach((card) => {
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
    });
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
  if (!TOUCH && !REDUCED) {
    const hero = document.getElementById("home");
    if (hero) {
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
    }
  }

  initSliders({ hasGsap, REDUCED, faDigits });
  initMediaCards({ hasGsap, REDUCED, fmtTime });
  initPortfolioFilter({ hasGsap, REDUCED, faDigits });
  initMarquees();
  initStatCounts({ hasGsap, ScrollTrigger });
  initBuildBars({ hasGsap, ScrollTrigger });
  initGpsDraw({ hasGsap, ScrollTrigger, REDUCED });
  initFaq();

  window.addEventListener("load", () => {
    if (hasGsap && ScrollTrigger) ScrollTrigger.refresh();
  });
}

/* ------------------------------------------------------- testimonial slider */

function initSliders({ hasGsap, REDUCED, faDigits }) {
  const slider = document.getElementById("t-slider");
  if (!slider) return;

  const cards = [...slider.querySelectorAll(".t-card")];
  const dotsWrap = document.getElementById("t-dots");
  if (!cards.length || !dotsWrap) return;
  const dots = cards.map((_, i) => {
    const d = document.createElement("button");
    d.className = "t-dot" + (i === 0 ? " active" : "");
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
  const nextBtn = document.getElementById("t-next");
  const prevBtn = document.getElementById("t-prev");
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
  let dragging = false;
  let startX = 0;
  let startSL = 0;
  let moved = 0;
  slider.addEventListener("pointerdown", (e) => {
    if (e.pointerType !== "mouse") return;
    dragging = true;
    moved = 0;
    startX = e.clientX;
    startSL = slider.scrollLeft;
    slider.classList.add("dragging");
    slider.setPointerCapture(e.pointerId);
  });
  slider.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    const dx = e.clientX - startX;
    moved = Math.max(moved, Math.abs(dx));
    slider.scrollLeft = startSL + dx;
  });
  const endDrag = () => {
    if (!dragging) return;
    dragging = false;
    slider.classList.remove("dragging");
  };
  slider.addEventListener("pointerup", endDrag);
  slider.addEventListener("pointercancel", endDrag);
  slider.addEventListener(
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
  const pfGrid = document.getElementById("pf-grid");
  const pfFilters = document.getElementById("pf-filters");
  const pfCount = document.getElementById("pf-count");
  const pfEmpty = document.getElementById("pf-empty");
  if (!pfGrid || !pfFilters) return;

  const items = [...pfGrid.querySelectorAll(".pf-item")];

  const apply = (cat) => {
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
            onComplete: () => el.classList.add("is-hidden"),
          });
        }
      } else {
        el.classList.toggle("is-hidden", !match);
      }
    });
    if (pfCount) pfCount.textContent = `${faDigits(shown)} PROJECTS`;
    if (pfEmpty) pfEmpty.classList.toggle("hidden", shown > 0);
  };

  pfFilters.addEventListener("click", (e) => {
    const btn = e.target.closest(".flt-btn");
    if (!btn) return;
    pfFilters.querySelectorAll(".flt-btn").forEach((b) =>
      b.classList.remove("active"),
    );
    btn.classList.add("active");
    apply(btn.dataset.filter);
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
              el.textContent = faDigits(Math.round(obj.v)) + suffix;
            },
          }),
      });
    } else {
      el.textContent = faDigits(target) + suffix;
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

/* ------------------------------------------------------- HTMX + toast bridge */

// After an HTMX swap, if the new content carries a [data-toast] element,
// announce its message (used by the lead form and contact form success state).
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
