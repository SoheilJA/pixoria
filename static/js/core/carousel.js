/* کاروسل GSAP — حرکت نرم، دکمه/نقطه، autoplay اختیاری، RTL-safe */
import { $$ } from "./utils.js";

export function initCarousel(wrap, { perView = 3, gap = 24, autoplay = false, interval = 6000 } = {}) {
  if (!wrap) return;
  const track = wrap.querySelector(".carousel-track");
  if (!track) return;
  const slides = [...track.children];
  if (!slides.length) return;

  let idx = 0;
  let tween = null;
  let timer = null;

  const per = () => {
    const w = window.innerWidth;
    return w < 700 ? 1 : w < 1000 ? Math.min(2, perView) : perView;
  };
  const maxIdx = () => Math.max(0, slides.length - per());

  function layout() {
    const wrapW = track.parentElement.offsetWidth || track.offsetWidth;
    const slideW = (wrapW - gap * (per() - 1)) / per();
    track.style.display = "flex";
    track.style.gap = gap + "px";
    slides.forEach((s) => {
      s.style.flex = `0 0 ${slideW}px`;
      s.style.minWidth = slideW + "px";
    });
  }

  function go(i, immediate = false) {
    idx = Math.max(0, Math.min(i, maxIdx()));
    const slideW = slides[0].offsetWidth + gap;
    /* RTL: حرکت به سمت مثبت */
    const target = idx * slideW;
    if (tween) tween.kill();
    if (window.gsap && !immediate) {
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
      [...dots.children].forEach((d, di) => d.classList.toggle("active", di === idx));
    }
  }

  /* دکمه‌ها: اگر در قالب نبودند بساز */
  if (!wrap.querySelector(".carousel-btn-prev, .carousel-btn-next")) {
    const nav = document.createElement("div");
    nav.className = "carousel-nav";
    nav.innerHTML =
      '<button type="button" class="carousel-btn-prev" aria-label="قبلی">→</button><button type="button" class="carousel-btn-next" aria-label="بعدی">←</button>';
    wrap.appendChild(nav);
  }
  if (!wrap.querySelector(".carousel-dots")) {
    const dots = document.createElement("div");
    dots.className = "carousel-dots";
    wrap.appendChild(dots);
  }
  const dotsWrap = wrap.querySelector(".carousel-dots");
  dotsWrap.innerHTML = "";

  const prev = wrap.querySelector(".carousel-btn-prev");
  const next = wrap.querySelector(".carousel-btn-next");
  if (prev) prev.addEventListener("click", () => { stopAuto(); go(idx - 1); });
  if (next) next.addEventListener("click", () => { stopAuto(); go(idx + 1); });

  function buildDots() {
    if (!dotsWrap) return;
    dotsWrap.innerHTML = "";
    for (let i = 0; i <= maxIdx(); i++) {
      const d = document.createElement("button");
      d.type = "button";
      d.className = "carousel-dot";
      d.setAttribute("aria-label", "اسلاید " + (i + 1));
      d.addEventListener("click", () => { stopAuto(); go(i); });
      dotsWrap.appendChild(d);
    }
  }

  function startAuto() {
    if (!autoplay) return;
    stopAuto();
    timer = setInterval(() => {
      go(idx >= maxIdx() ? 0 : idx + 1);
    }, interval);
  }
  function stopAuto() {
    if (timer) clearInterval(timer);
    timer = null;
  }

  /* لمس */
  let touchX = 0;
  track.addEventListener("touchstart", (e) => { touchX = e.changedTouches[0].screenX; stopAuto(); }, { passive: true });
  track.addEventListener("touchend", (e) => {
    const dx = e.changedTouches[0].screenX - touchX;
    if (dx < -50) go(idx + 1);
    else if (dx > 50) go(idx - 1);
    startAuto();
  }, { passive: true });

  wrap.addEventListener("mouseenter", stopAuto);
  wrap.addEventListener("mouseleave", startAuto);

  let rt;
  window.addEventListener("resize", () => {
    clearTimeout(rt);
    rt = setTimeout(() => { layout(); buildDots(); go(idx, true); }, 150);
  });

  layout();
  buildDots();
  go(0, true);
  startAuto();
}

export function initCarousels() {
  const byId = (id, opts) => initCarousel(document.getElementById(id), opts);
  byId("works-carousel", { perView: 4, gap: 24 });
  byId("testimonials-carousel", { perView: 3, gap: 20, autoplay: true, interval: 6000 });
  byId("latest-articles-carousel", { perView: 4, gap: 24 });
  /* هر کاروسل بدون id */
  $$(".carousel").forEach((el) => {
    if (!el.id) initCarousel(el, { perView: 3 });
  });
}
