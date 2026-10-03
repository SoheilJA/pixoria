/* Mobile nav — full-screen glass overlay.
   Open/close: CSS slides the panel, GSAP staggers the links (skipped under
   reduced-motion; classes alone show/hide everything). Body scroll lock, ESC
   to close, focus is moved into the menu and trapped while open, and the
   toggle gets focus back on close.
   HTMX swaps the whole <body>, so this re-inits on htmx:afterSwap. */
import { RM } from "./utils.js";

const G = window.gsap || null;

export function initMobileNav() {
  const nav = document.getElementById("mobile-nav");
  const toggle = document.querySelector(".menu-toggle");
  if (!nav || !toggle || nav.dataset.mobileNavInit) return;
  nav.dataset.mobileNavInit = "1";

  const closeBtn = nav.querySelector(".mobile-close");
  const links = [...nav.querySelectorAll(".mobile-link, .mobile-nav__foot > *")];
  let open = false;

  const focusables = () =>
    [...nav.querySelectorAll('a[href], button')].filter((el) => el.offsetParent !== null);

  const setOpen = (state) => {
    if (state === open) return;
    open = state;
    nav.classList.toggle("open", state);
    nav.setAttribute("aria-hidden", String(!state));
    toggle.setAttribute("aria-expanded", String(state));
    document.body.style.overflow = state ? "hidden" : "";

    if (G && !RM) {
      if (state) {
        G.from(links, {
          y: 26,
          opacity: 0,
          duration: 0.5,
          stagger: 0.055,
          ease: "power3.out",
          delay: 0.12,
        });
      } else {
        G.to(links, {
          y: -14,
          opacity: 0,
          duration: 0.22,
          stagger: 0.03,
          ease: "power2.in",
        });
        /* Clear the inline props once the panel has finished sliding out so
           the next open starts from a clean state. */
        G.delayedCall(0.62, () => G.set(links, { clearProps: "all" }));
      }
    }

    if (state) {
      const first = focusables()[0];
      if (first) first.focus();
    } else {
      toggle.focus();
    }
  };

  toggle.addEventListener("click", () => setOpen(!open));
  if (closeBtn) closeBtn.addEventListener("click", () => setOpen(false));

  nav.querySelectorAll(".mobile-link").forEach((a) =>
    a.addEventListener("click", () => setOpen(false)),
  );

  document.addEventListener("keydown", (e) => {
    if (!open) return;
    if (e.key === "Escape") {
      e.preventDefault();
      setOpen(false);
      return;
    }
    if (e.key !== "Tab") return;
    const f = focusables();
    if (!f.length) return;
    const first = f[0];
    const last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  });
}

initMobileNav();
document.addEventListener("htmx:afterSwap", initMobileNav);
