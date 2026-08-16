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

  // ─── Mobile nav toggle ───
  const toggle = document.querySelector('.menu-toggle');
  const nav    = document.querySelector('.mobile-nav');
  const close  = document.querySelector('.mobile-close');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
    });
    if (close) {
      close.addEventListener('click', () => {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      });
    }
    nav.querySelectorAll('a').forEach((a) =>
      a.addEventListener('click', () => {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      })
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
  if (val.length >= 4)  b1.classList.add('active-1');
  if (val.length >= 8)  b2.classList.add('active-2');
  if (val.length >= 12 && /[A-Z0-9!@#$]/.test(val)) b3.classList.add('active-3');
}

// ═══════════════════════════════════════════════
//  Carousel — vanilla JS, no dependencies
// ═══════════════════════════════════════════════
(function () {

  // تعداد اسلاید قابل نمایش بر اساس عرض صفحه
  function visibleCount(defaultCount) {
    const w = window.innerWidth;
    if (w <= 480)  return 1;
    if (w <= 768)  return Math.min(defaultCount, 2);
    if (w <= 1024) return Math.min(defaultCount, 3);
    return defaultCount;
  }

  function initCarousel(wrap, opts) {
    var track       = wrap.querySelector('.carousel-track');
    var prevBtn     = wrap.querySelector('.carousel-btn-prev');
    var nextBtn     = wrap.querySelector('.carousel-btn-next');
    var dotsWrap    = wrap.querySelector('.carousel-dots');

    if (!track) return;

    var slides      = Array.from(track.children);
    var total       = slides.length;
    var current     = 0;
    var perView     = visibleCount(opts.perView || 3);
    var gap         = opts.gap || 20;
    var autoTimer   = null;

    // ─── layout slides ───
    function layout() {
      perView = visibleCount(opts.perView || 3);
      var wrapWidth = track.parentElement.offsetWidth;
      var slideW = (wrapWidth - gap * (perView - 1)) / perView;

      track.style.display = 'flex';
      track.style.gap = gap + 'px';

      slides.forEach(function (s) {
        s.style.flex    = '0 0 ' + slideW + 'px';
        s.style.width   = slideW + 'px';
        s.style.minWidth = slideW + 'px';
      });
    }

    // ─── move to slide index ───
    function goTo(idx) {
      var max = total - perView;
      if (max < 0) max = 0;
      current = Math.max(0, Math.min(idx, max));

      var slideW = slides[0].offsetWidth + gap;
      // RTL: حرکت به راست مثبت است
      track.style.transform = 'translateX(' + (current * slideW) + 'px)';
      updateDots();
      updateBtns();
    }

    function prev() { goTo(current - 1); }
    function next() { goTo(current + 1); }

    // ─── dots ───
    function buildDots() {
      if (!dotsWrap) return;
      dotsWrap.innerHTML = '';
      var dotCount = Math.max(1, total - perView + 1);
      for (var i = 0; i < dotCount; i++) {
        var btn = document.createElement('button');
        btn.setAttribute('aria-label', 'اسلاید ' + (i + 1));
        btn.type = 'button';
        (function (idx) {
          btn.addEventListener('click', function () { goTo(idx); });
        })(i);
        dotsWrap.appendChild(btn);
      }
    }

    function updateDots() {
      if (!dotsWrap) return;
      Array.from(dotsWrap.children).forEach(function (d, i) {
        d.classList.toggle('active', i === current);
      });
    }

    function updateBtns() {
      var max = total - perView;
      if (prevBtn) prevBtn.disabled = current <= 0;
      if (nextBtn) nextBtn.disabled = current >= max;
    }

    // ─── autoplay ───
    function startAuto() {
      if (!opts.autoplay) return;
      autoTimer = setInterval(function () {
        if (current >= total - perView) goTo(0);
        else next();
      }, opts.interval || 5000);
    }
    function stopAuto() { clearInterval(autoTimer); }

    // ─── events ───
    if (prevBtn) prevBtn.addEventListener('click', function () { stopAuto(); prev(); startAuto(); });
    if (nextBtn) nextBtn.addEventListener('click', function () { stopAuto(); next(); startAuto(); });

    // swipe
    var touchX = 0;
    track.addEventListener('touchstart', function (e) {
      touchX = e.changedTouches[0].screenX;
    }, { passive: true });
    track.addEventListener('touchend', function (e) {
      var dx = e.changedTouches[0].screenX - touchX;
      // RTL: swipe چپ = next، swipe راست = prev
      if (dx < -50)  { stopAuto(); next(); startAuto(); }
      if (dx >  50)  { stopAuto(); prev(); startAuto(); }
    }, { passive: true });

    // pause on hover
    wrap.addEventListener('mouseenter', stopAuto);
    wrap.addEventListener('mouseleave', startAuto);

    // resize
    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        layout();
        buildDots();
        goTo(0);
      }, 150);
    });

    // ─── init ───
    layout();
    buildDots();
    goTo(0);
    startAuto();
  }

  // ─── راه‌اندازی بعد از لود DOM ───
  document.addEventListener('DOMContentLoaded', function () {
    // کاروسل نمونه‌کارها
    var worksWrap = document.getElementById('works-carousel');
    if (worksWrap) {
      initCarousel(worksWrap, { perView: 3, gap: 24, autoplay: false });
    }

    // کاروسل نظرات
    var testimonialsWrap = document.getElementById('testimonials-carousel');
    if (testimonialsWrap) {
      initCarousel(testimonialsWrap, { perView: 2, gap: 24, autoplay: true, interval: 5000 });
    }
  });

})();
