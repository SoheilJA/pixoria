/* موشن هدر بالای سایت — جمع‌شدن هنگام اسکرول + مگامنو خدمات
   reduced-motion: انیمیشن‌ها غیرفعال، منو همیشه قابل دسترس است */
import { RM } from "./utils.js";

const G = window.gsap || null;

export function initHeaderMotion() {
  const header = document.getElementById("site-header");
  if (!header || header.dataset.headerInit) return;
  header.dataset.headerInit = "1";

  /* ── جمع‌شدن هدر هنگام اسکرول ── */
  let lastY = window.scrollY;
  let ticking = false;

  function onScroll() {
    const y = window.scrollY;
    const shrinking = y > 24;
    header.classList.toggle("is-scrolled", shrinking);
    /* هدر مخفی هنگام اسکرول سریع به پایین */
    const hiding = y > 300 && y - lastY > 6;
    const showing = y - lastY < -6 || y < 300;
    if (hiding) header.classList.add("is-hidden");
    else if (showing) header.classList.remove("is-hidden");
    lastY = y;
    ticking = false;
  }

  window.addEventListener(
    "scroll",
    () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(onScroll);
      }
    },
    { passive: true },
  );
  onScroll();

  /* برگرداندن هدر وقتی موس روی ناحیه‌ی بالای صفحه است */
  header.addEventListener("mouseenter", () => header.classList.remove("is-hidden"));
  window.addEventListener("mousemove", (e) => {
    if (e.clientY < 40) header.classList.remove("is-hidden");
  }, { passive: true });

  /* ── مگامنو خدمات ── */
  const mega = header.querySelector("[data-megamenu]");
  if (!mega) return;
  const trigger = mega.querySelector("[data-mm-trigger]");
  const panel = mega.querySelector("[data-mm-panel]");
  const chevron = mega.querySelector(".mm-chevron");
  if (!trigger || !panel) return;

  let open = false;
  let hoverTimer = null;

  function setOpen(state) {
    if (state === open) return;
    open = state;
    trigger.setAttribute("aria-expanded", String(state));
    panel.classList.toggle("is-open", state);
    if (chevron) chevron.style.transform = state ? "rotate(180deg)" : "";

    if (state) {
      /* ورود: فید + لغزش پایین + stagger آیتم‌ها */
      if (G && !RM) {
        G.fromTo(
          panel,
          { autoAlpha: 0, y: -10 },
          { autoAlpha: 1, y: 0, duration: 0.28, ease: "power2.out" },
        );
        G.fromTo(
          panel.querySelectorAll(".mm-item"),
          { y: 10, autoAlpha: 0 },
          {
            y: 0,
            autoAlpha: 1,
            duration: 0.34,
            stagger: 0.045,
            ease: "power2.out",
            delay: 0.04,
          },
        );
      }
    } else if (G && !RM) {
      G.to(panel, { autoAlpha: 0, y: -8, duration: 0.2, ease: "power2.in" });
    }
  }

  /* دسکتاپ: hover با تاخیر کوتاه */
  mega.addEventListener("mouseenter", () => {
    clearTimeout(hoverTimer);
    if (matchMedia("(hover: hover) and (pointer: fine)").matches)
      hoverTimer = setTimeout(() => setOpen(true), 120);
  });
  mega.addEventListener("mouseleave", () => {
    clearTimeout(hoverTimer);
    hoverTimer = setTimeout(() => setOpen(false), 180);
  });

  /* کلیک/کیبورد */
  trigger.addEventListener("click", (e) => {
    e.preventDefault();
    setOpen(!open);
  });
  trigger.addEventListener("focus", () => setOpen(true));

  /* بستن با Esc یا کلیک بیرون */
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && open) {
      setOpen(false);
      trigger.focus();
    }
  });
  document.addEventListener("click", (e) => {
    if (open && !mega.contains(e.target)) setOpen(false);
  });

  /* focus trap سبک: آخرین لینک با Tab به trigger برمی‌گردد */
  panel.addEventListener("keydown", (e) => {
    if (e.key !== "Tab") return;
    const links = [...panel.querySelectorAll("a")].filter((a) => a.offsetParent !== null);
    if (!links.length) return;
    const first = links[0];
    const last = links[links.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      trigger.focus();
    }
  });
}
