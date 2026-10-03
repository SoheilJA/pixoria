/* Home page motion — GSAP: hero intro timeline, mouse parallax, the optional
   Three.js hero scene, marquee icon wave.
   Under prefers-reduced-motion every animation is skipped and the content is
   left fully visible. */
import { RM } from "./utils.js";

const G = window.gsap || null;

/* Hero 3D scene — locally served Three.js, loaded on demand. */
async function initHero3D(hero) {
  if (!hero || RM) return;
  try {
    const THREE = await import("../vendor/three.module.js");
    window.THREE = THREE;
    const { initHeroScene } = await import("../engine/scene.js");
    initHeroScene(hero);
  } catch (e) {
    /* Three.js unavailable — the scene is optional, fail silently. */
  }
}

export function initHomeMotion() {
  if (!G || RM) {
    /* No animation — keep the content visible and untouched. */
    document.querySelectorAll(".hm-anim").forEach((el) => {
      el.style.opacity = "1";
      el.style.transform = "none";
    });
    return;
  }

  /* Guard against re-initialising the same hero (htmx:afterSwap). */
  const hero = document.querySelector("section[aria-label='معرفی برند']");
  if (hero && hero.dataset.motionInit) return;
  if (hero) hero.dataset.motionInit = "1";

  /* ---- Hero entrance: title, grid, CTAs, marquee.
     (The data-reveal entrance animations are handled by core/reveal.js so the
     two never fight over the same elements.) ---- */
  const tl = G.timeline({ defaults: { ease: "power3.out" } });
  tl.from(".hero-title", { y: 44, opacity: 0, duration: 0.85 })
    .from(
      ".home-hero-grid > *",
      { y: 26, opacity: 0, duration: 0.65, stagger: 0.12 },
      "-=0.55",
    )
    .from(".home-hero-cta .btn", { y: 16, opacity: 0, duration: 0.45, stagger: 0.08 }, "-=0.3")
    .from(".home-marquee", { opacity: 0, duration: 0.7 }, "-=0.2");

  /* ---- Mouse parallax on the title and the marquee ---- */
  initHero3D(hero);
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

  /* ---- Breathing availability badge ---- */
  const badge = document.querySelector(
    "section[aria-label='معرفی برند'] .rounded-full.border-lime\\/40",
  );
  if (badge)
    G.to(badge, {
      scale: 1.06,
      transformOrigin: "center",
      duration: 1.4,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut",
    });

  /* ---- Gentle wave on the marquee lime accents ---- */
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
