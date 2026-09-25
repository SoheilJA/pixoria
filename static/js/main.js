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

  // ─── Mobile nav toggle — GSAP ───
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.mobile-nav');
  const close = document.querySelector('.mobile-close');
  if (toggle && nav) {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const G = window.gsap || null;
    let open = false;

    const setOpen = (state) => {
      open = state;
      nav.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
      if (G && !reduced) {
        if (open) {
          G.fromTo(nav, { xPercent: -100 }, { xPercent: 0, duration: 0.45, ease: 'power3.out' });
          G.from(nav.querySelectorAll('a, button.mobile-close'), {
            y: 26, opacity: 0, duration: 0.45, stagger: 0.06, ease: 'power2.out', delay: 0.1,
          });
        } else {
          G.to(nav, { xPercent: -100, duration: 0.35, ease: 'power3.in', onComplete: () => G.set(nav, { clearProps: 'all' }) });
        }
      }
    };

    toggle.addEventListener('click', () => setOpen(!open));
    if (close) close.addEventListener('click', () => setOpen(false));
    nav.querySelectorAll('a').forEach((a) =>
      a.addEventListener('click', () => setOpen(false))
    );
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

  // ─── Active mobile nav ───
  document.querySelectorAll('.rail-nav a.active').forEach((activeLink) => {
    const href = activeLink.getAttribute('href');
    document.querySelectorAll('.mobile-nav a').forEach((mLink) => {
      if (mLink.getAttribute('href') === href) mLink.classList.add('active');
    });
  });

  // ─── Year stamp ───
  document.querySelectorAll('[data-year]').forEach((el) => {
    el.textContent = String(new Date().getFullYear());
  });
})();

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

// ─── Carousels — GSAP module ───
if (document.querySelector('.carousel')) {
  import('./core/carousel.js')
    .then((m) => m.initCarousels())
    .catch(() => {});
}