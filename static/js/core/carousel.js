/* کاروسل سبک برای نمونه‌کارها و نظرات — بدون وابستگی */
import { $$ } from "./utils.js";
import { Sound } from "./sound.js";

export function initCarousel(wrap, { perView = 3, gap = 18 } = {}) {
  if (!wrap) return;
  const track = wrap.querySelector(".carousel-track");
  if (!track) return;
  const slides = [...track.children];
  if (slides.length <= 1) return;
  let idx = 0;

  const per = () => {
    const w = window.innerWidth;
    return w < 700 ? 1 : w < 1000 ? Math.min(2, perView) : perView;
  };
  const maxIdx = () => Math.max(0, slides.length - per());

  function go(i) {
    idx = Math.max(0, Math.min(i, maxIdx()));
    const slideW = slides[0].offsetWidth + gap;
    track.style.transform = `translateX(${idx * slideW * -1}px)`;
    const prev = wrap.querySelector(".carousel-btn-prev");
    const next = wrap.querySelector(".carousel-btn-next");
    if (prev) prev.disabled = idx === 0;
    if (next) next.disabled = idx === maxIdx();
    const dots = wrap.querySelector(".carousel-dots");
    if (dots) {
      [...dots.children].forEach((d, di) =>
        d.classList.toggle("on", di === idx),
      );
    }
  }

  let btns = wrap.querySelectorAll(".carousel-btn-prev, .carousel-btn-next");
  if (!btns.length) {
    const nav = document.createElement("div");
    nav.className = "carousel-nav";
    nav.innerHTML =
      '<button type="button" class="carousel-btn-prev" aria-label="قبلی">→</button><button type="button" class="carousel-btn-next" aria-label="بعدی">←</button>';
    wrap.appendChild(nav);
    if (!wrap.querySelector(".carousel-dots")) {
      const dots = document.createElement("div");
      dots.className = "carousel-dots";
      wrap.appendChild(dots);
    }
  }
  const prev = wrap.querySelector(".carousel-btn-prev");
  const next = wrap.querySelector(".carousel-btn-next");
  if (prev) prev.addEventListener("click", () => { go(idx - 1); Sound.blip(); });
  if (next) next.addEventListener("click", () => { go(idx + 1); Sound.blip(); });

  const dotsWrap = wrap.querySelector(".carousel-dots");
  if (dotsWrap) {
    dotsWrap.innerHTML = "";
    for (let i = 0; i <= maxIdx(); i++) {
      const d = document.createElement("button");
      d.type = "button";
      d.className = "carousel-dot";
      d.setAttribute("aria-label", "اسلاید " + (i + 1));
      d.addEventListener("click", () => go(i));
      dotsWrap.appendChild(d);
    }
  }

  window.addEventListener("resize", () => go(idx));
  go(0);
}

export function initCarousels() {
  $$(".carousel").forEach((el) => initCarousel(el, { perView: 3 }));
}
