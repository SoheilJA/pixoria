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
    let closeTween = null;

    const setOpen = (state) => {
      if (state === open) return;
      open = state;
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
      if (closeTween) { closeTween.kill(); closeTween = null; }
      const items = nav.querySelectorAll('a, button.mobile-close');
      if (G && !reduced) {
        if (open) {
          nav.classList.add('open');
          G.fromTo(nav, { xPercent: -100 }, { xPercent: 0, duration: 0.45, ease: 'power3.out' });
          G.from(items, { y: 26, opacity: 0, duration: 0.45, stagger: 0.06, ease: 'power2.out', delay: 0.1 });
        } else {
          closeTween = G.to(items, {
            y: 26, opacity: 0, duration: 0.3, stagger: { each: 0.04, from: 'end' }, ease: 'power2.in',
            onComplete: () => {
              closeTween = G.to(nav, {
                xPercent: -100, duration: 0.4, ease: 'power3.in',
                onComplete: () => {
                  nav.classList.remove('open');
                  G.set([nav, items], { clearProps: 'all' });
                },
              });
            },
          });
        }
      } else {
        nav.classList.toggle('open', open);
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

// ─── Carousels — GSAP module ───
if (document.querySelector('.carousel')) {
  import('./core/carousel.js')
    .then((m) => m.initCarousels())
    .catch(() => {});
}