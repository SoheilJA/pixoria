/* موشن صفحه‌ی خانه — GSAP + پارالاکس ماوس، ورود هیرو، شمارنده‌ها
   reduced-motion: همه‌ی حرکت‌ها غیرفعال و محتوا کامل نمایش داده می‌شود */
import { RM } from "./utils.js";

const G = window.gsap || null;

export function initHomeMotion() {
  if (!G || RM) {
    /* بدون انیمیشن — محتوا همیشه کامل و قابل‌مشاهده */
    document.querySelectorAll(".hm-anim").forEach((el) => {
      el.style.opacity = "1";
      el.style.transform = "none";
    });
    return;
  }

  /* ---- ورود هیرو: تیتر، lead، دکمه‌ها، مارکی ---- */
  const tl = G.timeline({ defaults: { ease: "power3.out" } });
  tl.from(".hero-title", { y: 44, opacity: 0, duration: 0.85 })
    .from(
      ".home-kicker, [data-aos='fade-down']",
      { y: -16, opacity: 0, duration: 0.5 },
      "-=0.6",
    )
    .from(
      ".home-hero-grid > *",
      { y: 26, opacity: 0, duration: 0.65, stagger: 0.12 },
      "-=0.35",
    )
    .from(".home-hero-cta .btn", { y: 16, opacity: 0, duration: 0.45, stagger: 0.08 }, "-=0.3")
    .from(".home-marquee", { opacity: 0, duration: 0.7 }, "-=0.2");

  /* ---- پارالاکس ماوس روی تیتر و مارکی ---- */
  const hero = document.querySelector("section[aria-label='معرفی برند']");
  if (hero && matchMedia("(hover: hover) and (pointer: fine)").matches) {
    const targets = [
      { el: hero.querySelector(".hero-title"), depth: 18 },
      { el: hero.querySelector(".home-marquee"), depth: -10 },
    ].filter((t) => t.el);
    const setter = targets.map((t) => ({
      x: G.quickSetter(t.el, "x", "px"),
      y: G.quickSetter(t.el, "y", "px"),
      depth: t.depth,
    }));
    hero.addEventListener("mousemove", (e) => {
      const r = hero.getBoundingClientRect();
      const nx = (e.clientX - r.left) / r.width - 0.5;
      const ny = (e.clientY - r.top) / r.height - 0.5;
      setter.forEach((s) => {
        s.x(nx * s.depth);
        s.y(ny * s.depth * 0.6);
      });
    });
    hero.addEventListener("mouseleave", () => {
      G.to(targets.map((t) => t.el), { x: 0, y: 0, duration: 0.6, ease: "power2.out" });
    });
  }

  /* ---- ظاهرشدن کارت‌ها با اسکرول (ScrollTrigger) ---- */
  if (window.ScrollTrigger) {
    document
      .querySelectorAll(".svc-card, section .group.flex.flex-col, .carousel-track > *")
      .forEach((el) => {
        G.from(el, {
          y: 30,
          opacity: 0,
          duration: 0.55,
          ease: "power2.out",
          scrollTrigger: { trigger: el, start: "top 92%", once: true },
        });
      });
  }

  /* ---- نفس کشیدن badge وضعیت همکاری ---- */
  const badge = document.querySelector(".rounded-full.bg-lime");
  if (badge)
    G.to(badge, {
      scale: 1.06,
      transformOrigin: "center",
      duration: 1.4,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut",
    });

  /* ---- موج ملایم آیکن‌های مارکی ---- */
  document.querySelectorAll(".home-marquee .text-lime").forEach((s, i) => {
    G.to(s, {
      y: -5,
      duration: 0.9 + (i % 3) * 0.15,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut",
      delay: i * 0.12,
    });
  });
}
