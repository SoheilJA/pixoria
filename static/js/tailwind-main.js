// Axioma — minimal vanilla JS: reveal-on-scroll + mobile nav + work filter
(function () {
  // Reveal on scroll (compositor-friendly: opacity + transform only)
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduced && "IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -8% 0px" },
    );
    document.querySelectorAll(".reveal").forEach((el) => io.observe(el));
  } else {
    document
      .querySelectorAll(".reveal")
      .forEach((el) => el.classList.add("in"));
  }

  // Mobile nav toggle
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".mobile-nav");
  const close = document.querySelector(".mobile-close");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.style.overflow = open ? "hidden" : "";
    });
    if (close) {
      close.addEventListener("click", () => {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
      });
    }
    nav.querySelectorAll("a").forEach((a) =>
      a.addEventListener("click", () => {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
      }),
    );
  }

  // Work filter (work.html)
  const filterButtons = document.querySelectorAll(".work-filters button");
  const grid = document.querySelector(".work-grid");
  if (filterButtons.length && grid) {
    filterButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const filter = btn.getAttribute("data-filter");
        filterButtons.forEach((b) =>
          b.setAttribute("aria-pressed", b === btn ? "true" : "false"),
        );
        grid.querySelectorAll("article").forEach((article) => {
          const tags = (article.getAttribute("data-tags") || "").split(",");
          const show = filter === "all" || tags.includes(filter);
          article.style.display = show ? "" : "none";
        });
      });
    });
  }

  // Year stamp in footer
  document.querySelectorAll("[data-year]").forEach((el) => {
    el.textContent = String(new Date().getFullYear());
  });
})();

// Active nav link based on current page
(function () {
  const links = document.querySelectorAll(".rail-nav a");
  const currentPath = window.location.pathname;

  links.forEach((link) => {
    const href = link.getAttribute("href");

    if (currentPath.endsWith(href)) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
})();



function updateStrength(val) {
        const b1 = document.getElementById("bar1");
        const b2 = document.getElementById("bar2");
        const b3 = document.getElementById("bar3");
        [b1, b2, b3].forEach((b) => (b.className = "bar"));
        if (val.length >= 4) b1.classList.add("active-1");
        if (val.length >= 8) b2.classList.add("active-2");
        if (val.length >= 12 && /[A-Z0-9!@#$]/.test(val))
          b3.classList.add("active-3");
      }