/* Global motion layer — data-* driven, GSAP-powered, HTMX-safe.
   This is the site's one motion entry point; it runs the scroll reveals
   (core/reveal.js) plus every pointer/scroll effect:

     data-reveal="up|down|left|right|fade|blur"   scroll reveal (once)
     data-reveal-delay="ms" / data-reveal-duration="ms"
     data-split            word-by-word heading reveal (Persian-safe)
     data-parallax="0.2"   scroll-linked vertical drift (viewport fraction;
                           negative inverts). Best on decorative layers.
     data-tilt             pointer 3D tilt + glare (writes CSS custom
                           properties only, so it composes with data-reveal,
                           which clears its transform when it finishes)
     data-tilt-max="10"    max tilt in degrees (default 8)
     data-magnetic="12"    button magnetic pull in px (default 10)
     data-counter="1234"   count-up when scrolled into view
       data-counter-decimals="1"  data-counter-prefix="+"  data-counter-suffix="٪"
       data-counter-locale="fa"   (default) Persian digits — "en" for Latin
     data-bar="85"         animates the element's width to this percent when
                           it scrolls into view (skill-bar fill)
     data-horizontal      pinned section; its [data-horizontal-track] is
                           translated sideways as the page scrolls (desktop
                           only — see data-horizontal-min). The track is a
                           plain stacked grid below that width.
     data-horizontal-min="1024"  breakpoint for the pinned horizontal mode
     #scroll-progress      slim brand-green scroll progress bar (in the header)

   Rules: never combine data-magnetic with data-reveal (both own the element's
   transform). Everything no-ops under prefers-reduced-motion (counters jump
   to their final value) and pointer effects are skipped on coarse pointers.
   The whole layer re-scans after every htmx:afterSwap. */
import { $$, G, RM } from "./utils.js";
import { initReveals, installRevealSafetyNet } from "./core/reveal.js";

const FINE = matchMedia("(hover: hover) and (pointer: fine)").matches;

/* ── Scroll progress bar ── */
function initScrollProgress() {
  const bar = document.getElementById("scroll-progress");
  if (!bar || bar.__progressInit || !window.ScrollTrigger) return;
  bar.__progressInit = true;
  G.fromTo(
    bar,
    { scaleX: 0 },
    {
      scaleX: 1,
      ease: "none",
      scrollTrigger: { scrub: 0.3, start: 0, end: "max" },
    },
  );
}

/* ── Parallax: the element drifts by `speed * viewport height` as it crosses
   the viewport. Decorative only — keep it off text-heavy containers. ── */
function initParallax(root = document) {
  $$("[data-parallax]", root)
    .filter((el) => !el.__parallaxDone)
    .forEach((el) => {
      el.__parallaxDone = true;
      const speed = parseFloat(el.dataset.parallax) || 0;
      if (!speed) return;
      const dist = () => (window.innerHeight || 800) * speed;
      G.fromTo(
        el,
        { y: () => -dist() / 2 },
        {
          y: () => dist() / 2,
          ease: "none",
          immediateRender: false,
          scrollTrigger: { trigger: el, scrub: 0.5, start: "top bottom", end: "bottom top" },
        },
      );
    });
}

/* ── 3D tilt + pointer glare, driven purely by CSS custom properties:
     --rx/--ry rotate, --gx/--gy place the specular highlight. ── */
function initTilt(root = document) {
  if (!FINE) return;
  $$("[data-tilt]", root)
    .filter((el) => !el.__tiltDone)
    .forEach((el) => {
      el.__tiltDone = true;
      const max = parseFloat(el.dataset.tiltMax) || 8;
      const onMove = (e) => {
        const r = el.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width;
        const py = (e.clientY - r.top) / r.height;
        /* CSS axes: +X right, +Y down. Positive rotateX brings the bottom
           edge toward the viewer, positive rotateY pushes the right edge
           away — so the element follows the pointer in both directions. */
        el.style.setProperty("--rx", ((py - 0.5) * 2 * max).toFixed(2) + "deg");
        el.style.setProperty("--ry", ((0.5 - px) * 2 * max).toFixed(2) + "deg");
        el.style.setProperty("--gx", (px * 100).toFixed(1) + "%");
        el.style.setProperty("--gy", (py * 100).toFixed(1) + "%");
      };
      const onLeave = () => {
        el.style.removeProperty("--rx");
        el.style.removeProperty("--ry");
      };
      el.addEventListener("pointermove", onMove, { passive: true });
      el.addEventListener("pointerleave", onLeave);
    });
}

/* ── Magnetic pull for buttons: translate toward the pointer, spring back. ── */
function initMagnetic(root = document) {
  if (!FINE) return;
  $$("[data-magnetic]", root)
    .filter((el) => !el.__magneticDone)
    .forEach((el) => {
      el.__magneticDone = true;
      const strength = parseFloat(el.dataset.magnetic) || 10;
      el.addEventListener(
        "pointermove",
        (e) => {
          const r = el.getBoundingClientRect();
          const x = (e.clientX - (r.left + r.width / 2)) / (r.width / 2);
          const y = (e.clientY - (r.top + r.height / 2)) / (r.height / 2);
          G.to(el, { x: x * strength, y: y * strength * 0.6, duration: 0.4, ease: "power3.out" });
        },
        { passive: true },
      );
      el.addEventListener("pointerleave", () => {
        G.to(el, { x: 0, y: 0, duration: 0.6, ease: "elastic.out(1, 0.35)" });
      });
    });
}

/* ── Number counters, formatted in Persian by default. ── */
function formatCount(value, el) {
  const decimals = parseInt(el.dataset.counterDecimals || "0", 10) || 0;
  const locale = el.dataset.counterLocale === "en" ? "en-US" : "fa-IR";
  const text = Number(value.toFixed(decimals)).toLocaleString(locale, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  return (el.dataset.counterPrefix || "") + text + (el.dataset.counterSuffix || "");
}

function initCounters(root = document) {
  $$("[data-counter]", root)
    .filter((el) => !el.__counterDone)
    .forEach((el) => {
      el.__counterDone = true;
      const target = parseFloat(el.dataset.counter);
      if (!Number.isFinite(target)) return;
      if (RM) {
        el.textContent = formatCount(target, el);
        return;
      }
      const obj = { v: 0 };
      G.to(obj, {
        v: target,
        duration: 1.6,
        ease: "power2.out",
        scrollTrigger: { trigger: el, start: "top 85%", once: true },
        onUpdate: () => {
          el.textContent = formatCount(obj.v, el);
        },
      });
    });
}

/* ── Skill bars: the element's width tweens from 0 to data-bar percent when
   it scrolls into view. Under reduced motion it jumps to the final width. ── */
function initBars(root = document) {
  $$("[data-bar]", root)
    .filter((el) => !el.__barDone)
    .forEach((el) => {
      el.__barDone = true;
      const pct = Math.min(100, Math.max(0, parseFloat(el.dataset.bar) || 0));
      el.style.width = "0%";
      if (RM) {
        el.style.width = pct + "%";
        return;
      }
      G.to(el, {
        width: pct + "%",
        duration: 1.3,
        ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 88%", once: true },
      });
    });
}

/* ── Pinned horizontal track: the section is pinned to the viewport while its
   wide inner track ([data-horizontal-track]) is translated sideways, so a row
   of cards is scrolled by scrolling down. Skipped under reduced motion and
   below `data-horizontal-min`, where the track is a plain stacked grid.
   Direction follows the document so RTL and LTR pages both scroll the right
   way. ── */
function initHorizontal(root = document) {
  $$("[data-horizontal]", root)
    .filter((el) => !el.__horizontalDone)
    .forEach((el) => {
      el.__horizontalDone = true;
      if (RM || !window.ScrollTrigger) return;
      const min = parseInt(el.dataset.horizontalMin || "1024", 10);
      if (!matchMedia(`(min-width: ${min}px)`).matches) return;
      const track = el.querySelector("[data-horizontal-track]");
      if (!track) return;
      const dir = getComputedStyle(el).direction === "rtl" ? 1 : -1;
      const distance = () => Math.max(0, track.scrollWidth - el.clientWidth);
      G.to(track, {
        x: () => dir * distance(),
        ease: "none",
        scrollTrigger: {
          trigger: el,
          start: "top top",
          end: () => "+=" + distance(),
          scrub: 0.5,
          pin: true,
          anticipatePin: 1,
          invalidateOnRefresh: true,
        },
      });
    });
}

/* ── Drop ScrollTriggers whose trigger element left the DOM in an HTMX swap,
   so page navigation does not pile up stale tweens. ── */
function pruneStaleTriggers() {
  if (!window.ScrollTrigger) return;
  window.ScrollTrigger.getAll().forEach((st) => {
    const t = st.trigger;
    if (t && !t.isConnected) st.kill();
  });
}

export function initMotion() {
  if (!G) return;
  initScrollProgress();
  initReveals();
  initParallax();
  initTilt();
  initMagnetic();
  initCounters();
  initBars();
  initHorizontal();
  installRevealSafetyNet();
}

function boot() {
  initMotion();
  /* htmx swaps the page body; re-scan the new content. */
  document.addEventListener("htmx:afterSwap", () => {
    pruneStaleTriggers();
    initMotion();
  });
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
else boot();
