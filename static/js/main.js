// Axioma — minimal vanilla JS
(function () {
  // ─── Reveal on scroll ───
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduced && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('in');
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
    );
    document.querySelectorAll('.reveal').forEach((el) => io.observe(el));
  } else {
    document.querySelectorAll('.reveal').forEach((el) => el.classList.add('in'));
  }

  // ─── Mobile nav (full-screen overlay) — static/js/core/mobile-nav.js ───
  if (document.getElementById("mobile-nav")) {
    import("./core/mobile-nav.js").catch(() => {});
  }

  // ─── Work filter ───
  const filterButtons = document.querySelectorAll('.work-filters button');
  const grid = document.querySelector('.work-grid');
  if (filterButtons.length && grid) {
    filterButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const filter = btn.getAttribute('data-filter');
        filterButtons.forEach((b) =>
          b.setAttribute('aria-pressed', b === btn ? 'true' : 'false')
        );
        grid.querySelectorAll('article').forEach((article) => {
          const tags = (article.getAttribute('data-tags') || '').split(',');
          article.style.display = filter === 'all' || tags.includes(filter) ? '' : 'none';
        });
      });
    });
  }

  // ─── Year stamp ───
  document.querySelectorAll('[data-year]').forEach((el) => {
    el.textContent = String(new Date().getFullYear());
  });
})();

// ─── Lucide icons are rendered server-side via {% icon %} (local SVG sprite) ───

// ─── Password strength ───
function updateStrength(val) {
  const b1 = document.getElementById('bar1');
  const b2 = document.getElementById('bar2');
  const b3 = document.getElementById('bar3');
  if (!b1) return;
  [b1, b2, b3].forEach((b) => (b.className = 'bar'));
  if (val.length >= 4) b1.classList.add('active-1');
  if (val.length >= 8) b2.classList.add('active-2');
  if (val.length >= 12 && /[A-Z0-9!@#$]/.test(val)) b3.classList.add('active-3');
}

// ─── Carousels — GSAP module (re-inits after every HTMX swap) ───
let carouselPromise = null;
function initCarousels() {
  if (!carouselPromise) carouselPromise = import('./core/carousel.js');
  carouselPromise
    .then((m) => m.initCarousels())
    .catch(() => {});
}
if (document.querySelector('.carousel')) initCarousels();
document.addEventListener('htmx:afterSwap', initCarousels);