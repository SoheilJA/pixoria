/* Carousel — the ONE carousel implementation for the whole site.
   Vanilla + GSAP. RTL-safe, touch swipe, autoplay, keyboard, dots/arrows,
   responsive per-view, and it re-initialises safely after an HTMX swap.

   Every option is declared as a data-* attribute on the wrapper by
   templates/components/carousel.html, so the markup stays declarative:
   data-per-view, data-gap, data-autoplay (1/0), data-interval,
   data-show-arrows (1/0), data-show-dots (1/0). */
import { $$, RM } from "./utils.js";

const DEFAULTS = {
  perView: 3,
  gap: 24,
  autoplay: false,
  interval: 6000,
  showArrows: true,
  showDots: true,
};

/* Active instances. Entries whose wrapper left the DOM (an HTMX swap
   replaced the page content) are pruned on the next init pass so their
   autoplay timer and resize listener do not outlive the element. */
const live = new Set();

function optsFrom(el) {
  const num = (k) => (el.dataset[k] !== undefined ? Number(el.dataset[k]) : DEFAULTS[k]);
  const flag = (k) => (el.dataset[k] !== undefined ? el.dataset[k] === "1" : DEFAULTS[k]);
  return {
    perView: Math.max(1, num("perView") || 3),
    gap: Math.max(0, num("gap") ?? 24),
    /* autoplay is motion — never run it under prefers-reduced-motion */
    autoplay: flag("autoplay") && !RM,
    interval: Math.max(2000, num("interval") || 6000),
    showArrows: flag("showArrows"),
    showDots: flag("showDots"),
  };
}

/* The arrow buttons are rendered by the template ({% icon %}); this is the
   fallback for a bare .carousel whose markup came from somewhere else. The
   sprite URL is read from an icon already on the page so the JS never
   hardcodes a static path and stays in sync with the template tag. */
function arrowButton(cls, icon, label) {
  const use = document.querySelector("svg use[href], svg use[xlink\\:href]");
  if (!use) return null;
  const ref = use.getAttribute("href") || use.getAttribute("xlink:href");
  if (!ref) return null;
  const svg =
    `<svg aria-hidden="true" focusable="false" class="h-5 w-5" fill="none" ` +
    `stroke="currentColor" stroke-width="2" stroke-linecap="round" ` +
    `stroke-linejoin="round" viewBox="0 0 24 24">` +
    `<use href="${ref.split("#")[0]}#i-${icon}" ` +
    `xlink:href="${ref.split("#")[0]}#i-${icon}"></use></svg>`;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = cls;
  btn.setAttribute("aria-label", label);
  btn.innerHTML = svg;
  return btn;
}

function ensureNav(wrap) {
  if (wrap.querySelector(".carousel-btn-prev, .carousel-btn-next")) return;
  const prev = arrowButton("carousel-btn-prev", "arrow-right", "اسلاید قبلی");
  const next = arrowButton("carousel-btn-next", "arrow-left", "اسلاید بعدی");
  if (!prev || !next) return;
  const nav = document.createElement("div");
  nav.className = "carousel-nav";
  nav.append(prev, next);
  wrap.appendChild(nav);
}

export function initCarousel(wrap, overrides = {}) {
  if (!wrap) return;
  if (wrap.dataset.carouselReady) return; // HTMX swap guard
  const opts = { ...optsFrom(wrap), ...overrides };
  const track = wrap.querySelector(".carousel-track");
  if (!track) return;
  const slides = [...track.children];
  if (!slides.length) return;

  wrap.dataset.carouselReady = "1";
  let idx = 0;
  let tween = null;
  let timer = null;
  let rt = null;

  const per = () => {
    const w = window.innerWidth;
    return w < 700 ? 1 : w < 1000 ? Math.min(2, opts.perView) : opts.perView;
  };
  const maxIdx = () => Math.max(0, slides.length - per());

  function layout() {
    const wrapW = track.parentElement.offsetWidth || track.offsetWidth;
    const slideW = (wrapW - opts.gap * (per() - 1)) / per();
    track.style.display = "flex";
    track.style.gap = opts.gap + "px";
    slides.forEach((s) => {
      s.style.flex = `0 0 ${slideW}px`;
      s.style.minWidth = slideW + "px";
    });
  }

  function go(i, immediate = false) {
    idx = Math.max(0, Math.min(i, maxIdx()));
    const slideW = slides[0].offsetWidth + opts.gap;
    /* RTL: the track starts at the right edge, so advancing shifts it
       rightward (positive translateX) to reveal the next slide. */
    const target = idx * slideW;
    if (tween) tween.kill();
    if (window.gsap && !immediate && !RM) {
      tween = window.gsap.to(track, {
        x: target,
        duration: 0.9,
        ease: "power3.inOut",
      });
    } else {
      track.style.transform = `translateX(${target}px)`;
    }
    updateUI();
  }

  function updateUI() {
    const prev = wrap.querySelector(".carousel-btn-prev");
    const next = wrap.querySelector(".carousel-btn-next");
    if (prev) prev.disabled = idx === 0;
    if (next) next.disabled = idx === maxIdx();
    const dots = wrap.querySelector(".carousel-dots");
    if (dots) {
      [...dots.children].forEach((d, di) => {
        d.classList.toggle("active", di === idx);
        d.setAttribute("aria-current", di === idx ? "true" : "false");
      });
    }
  }

  function startAuto() {
    if (!opts.autoplay) return;
    stopAuto();
    timer = setInterval(() => {
      if (document.hidden) return; // do not advance a tab nobody is watching
      go(idx >= maxIdx() ? 0 : idx + 1);
    }, opts.interval);
  }
  function stopAuto() {
    if (timer) clearInterval(timer);
    timer = null;
  }

  if (opts.showArrows) ensureNav(wrap);
  const prev = wrap.querySelector(".carousel-btn-prev");
  const next = wrap.querySelector(".carousel-btn-next");
  if (prev) prev.addEventListener("click", () => { stopAuto(); go(idx - 1); });
  if (next) next.addEventListener("click", () => { stopAuto(); go(idx + 1); });

  /* One dot per scroll position; built here because the slide count is only
     known once the track is in the DOM. */
  const dotsWrap = wrap.querySelector(".carousel-dots");
  function buildDots() {
    if (!dotsWrap) return;
    dotsWrap.innerHTML = "";
    for (let i = 0; i <= maxIdx(); i++) {
      const d = document.createElement("button");
      d.type = "button";
      d.setAttribute("aria-label", "اسلاید " + (i + 1));
      d.addEventListener("click", () => { stopAuto(); go(i); });
      dotsWrap.appendChild(d);
    }
  }
  if (!opts.showDots && dotsWrap) dotsWrap.remove();

  /* Touch swipe: dragging left advances (the next slide waits on the left). */
  let touchX = 0;
  track.addEventListener("touchstart", (e) => { touchX = e.changedTouches[0].screenX; stopAuto(); }, { passive: true });
  track.addEventListener("touchend", (e) => {
    const dx = e.changedTouches[0].screenX - touchX;
    if (dx < -50) go(idx + 1);
    else if (dx > 50) go(idx - 1);
    startAuto();
  }, { passive: true });

  /* Keyboard: ArrowLeft advances, ArrowRight goes back (RTL). Only acts when
     the focus is on the carousel chrome itself, so links inside the slides
     keep their normal arrow-key behaviour. */
  wrap.addEventListener("keydown", (e) => {
    const onChrome = e.target.closest(".carousel-nav, .carousel-dots, .carousel-track");
    if (!onChrome) return;
    if (e.key === "ArrowLeft") { e.preventDefault(); stopAuto(); go(idx + 1); }
    else if (e.key === "ArrowRight") { e.preventDefault(); stopAuto(); go(idx - 1); }
    else if (e.key === "Home") { e.preventDefault(); stopAuto(); go(0); }
    else if (e.key === "End") { e.preventDefault(); stopAuto(); go(maxIdx()); }
  });

  wrap.addEventListener("mouseenter", stopAuto);
  wrap.addEventListener("mouseleave", startAuto);

  const onResize = () => {
    clearTimeout(rt);
    rt = setTimeout(() => { layout(); buildDots(); go(idx, true); }, 150);
  };
  window.addEventListener("resize", onResize);

  live.add({
    wrap,
    destroy() {
      stopAuto();
      window.removeEventListener("resize", onResize);
      if (tween) tween.kill();
    },
  });

  layout();
  buildDots();
  go(0, true);
  startAuto();
}

export function initCarousels(root = document) {
  /* Drop carousels removed by an HTMX swap before initialising new ones. */
  for (const inst of [...live]) {
    if (!inst.wrap.isConnected) {
      inst.destroy();
      live.delete(inst);
    }
  }
  [...root.querySelectorAll(".carousel")].forEach((el) => initCarousel(el));
}
