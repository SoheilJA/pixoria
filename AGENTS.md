# AGENTS.md — Pixoria homepage redesign

Stack: Django 6 + Tailwind v4 + Three.js r160 + GSAP/ScrollTrigger + HTMX + vanilla JS.
Persian/RTL. All libraries served locally. Homepage only; service pages reuse
the shared modules later.

## Audit summary (existing homepage, keep working)

**Apps:** `core` (SiteSettings, SocialLink, About*, Proposal*), `home`
(HeroSection, HeroMarqueeItem, FeaturedWorkSection, ServicesSection,
ClientMarqueeItem, ManifestoSection, CTASection, LatestArticlesSection),
`portfolio`, `services`, `contact`, `blog`.

**Current homepage sections** (`templates/home/index.html`, view `apps/home/views.py:home`):
1. Hero — `HeroSection` + `HeroMarqueeItem` marquee, `.hero-title` intro timeline
2. Featured works — `FeaturedWorkSection` + `Portfolio.objects.filter(featured=True)`, carousel
3. Services — `ServicesSection` + featured `Service`, card grid
4. Clients — `ClientMarqueeItem` marquee
5. Manifesto — `ManifestoSection`
6. Testimonials — `ServiceTestimonial(show_on_home=True)`, carousel
7. Latest articles — `LatestArticlesSection` + published `Article`, carousel
8. Pre-footer CTA band + footer — `CTASection` / `SiteSettings` (in `base.html`)

**Shared infra (do not break):**
- `templates/base.html` — preloader (two panels + pixel wordmark, `sessionStorage['pixoriaPreloaded']`), `#htmx-progress`, glass header + services megamenu, `#mobile-nav`, footer, scripts. `hx-boost="true"` on `<body>` ⇒ whole body is swapped on navigation; every module re-inits on `htmx:afterSwap`.
- `static/js/motion.js` — canonical data-driven layer: `data-reveal`, `data-reveal-delay/-duration`, `data-split`, `data-parallax`, `data-tilt`, `data-magnetic`, `data-counter` (+prefix/suffix/decimals/locale). Use these instead of ad-hoc animations.
- `static/js/core/` — `reveal.js`, `carousel.js`, `header.js`, `home-motion.js`, `wordmark.js`, `glass.js`, `utils.js` (`$`, `$$`, `G`, `RM`, `store`, `sstep`…).
- `static/js/engine/scene.js` — hero wireframe planet. **Replaced** by the new page background; the file stays for now, its loader call is removed.
- `static/js/engine/footer-stars.js` — footer starfield (stays).
- `{% pixel_wordmark %}` (`apps/core/templatetags/brand_tags.py`) inlines SVGs built by `scripts/build_pixel_wordmark.py`.
- Design tokens in `static/src/input.css` (`@theme`): night/paper/ink/mist/line surfaces, lime scale, type scale, `--ease-ax…`. Tailwind build: `npm run build` (`static/src/input.css` → `static/css/tailwind.css`).
- Single H1 rule: the hero holds the only `<h1>`; sections use `<h2>` via `components/section_header.html`.

**Known bug (task §2):** the pixel wordmark renders «پ ی ک س و ر ی ا» separated because
PIL has no libraqm, so `build_pixel_wordmark.py` laid letters out one by one.
Fix: `arabic_reshaper` + `python-bidi` emit presentation forms that join without
raqm. Both are now installed and must be added to `requirements.txt`.

## Checklist

### Phase 0 — Audit
- [x] Audit templates, views, models, admin, static, Tailwind/i18n/build pipeline
- [x] Review reference image 1 (current), image 2 (structure reference) and the video brief
- [x] Verify `python manage.py check` passes; DB already seeded

### Phase 1 — Foundation
- [x] 1.1 Add `arabic_reshaper` + `python-bidi` to `requirements.txt`
- [x] 1.2 Vendor build-only dev deps nothing to add; verify Tailwind build runs
- [x] 1.3 Add pixel/glow design tokens + utilities to `static/src/input.css`, rebuild
- [x] 1.4 Add `bg-shell` container (`hx-preserve`) to `base.html` for the shared canvas
- [x] 1.5 Vendor Alpine.js for the FAQ accordion (local file, no CDN)

### Phase 2 — Background engine (`static/js/pixoria-bg/`)
- [x] 2.1 `PixoriaBackground` module skeleton: canvas, quality/fallback handling, dispose
- [x] 2.2 Ribbon geometry + GLSL shader (noise-driven flow, additive glow)
- [x] 2.3 Scroll driver: ScrollTrigger → uniforms; `data-bg-*` section keyframes
- [x] 2.4 Presets file (`home` + footer rest-state shared by every page)
- [x] 2.5 CSS gradient fallback (no WebGL / reduced motion / low-end), pause off-screen/tab-hidden
- [x] 2.6 Boot from `base.html` via `json_script` config; wire readability vignette

### Phase 3 — Preloader link
- [x] 3.1 Canvas shows inside the preloader in hero state on first visit
- [x] 3.2 On load done: same canvas transitions (pull-back/dim/move) into page bg, overlay fades
- [x] 3.3 Later visits / HTMX navigations: short path, canvas never restarts

### Phase 4 — Logo / wordmark
- [x] 4.1 Fix `build_pixel_wordmark.py` to render the joined word via reshaper+bidi
- [x] 4.2 Regenerate brand assets, verify «پیکسوریا» connects in header/preloader/footer
- [x] 4.3 Self-host a pixel Latin font (already present: `press-start-2p` / `jersey10`) wired for labels

### Phase 5 — Header + mobile menu
- [x] 5.1 Redesign header: floating liquid-glass bar, wordmark, nav, lime CTA, active indicator
- [x] 5.2 Hide on scroll-down / show on scroll-up, glass strengthens after scroll
- [x] 5.3 Full-screen mobile menu overlay (GSAP): staggered links, contact block, socials, CTA, scroll-lock, ESC, focus handling

### Phase 6 — Custom cursor
- [x] 6.1 `static/js/cursor.js`: dot + trailing ring (quickTo), states, `data-cursor` labels
- [x] 6.2 Magnetic CTA, click feedback, pixel trail; disabled on touch / reduced motion

### Phase 7 — Section system + sections
- [x] 7.1 `HomeSection` model (`key`, `order`, `is_active`) + admin; view renders in admin order
- [x] 7.2 `templates/home/sections/` partials; `home/index.html` includes them by order
- [x] 7.3 Hero restyle (pixel highlight word, stat chips, scroll indicator)
- [x] 7.4 Clients strip (reuse `ClientMarqueeItem`, pausable marquee)
- [x] 7.5 Stats/counters section (animated numbers via `data-counter`)
- [x] 7.6 Process section — pinned horizontal scroll desktop, stacked mobile
- [x] 7.7 Why Pixoria — bento grid with pixel micro-visuals
- [x] 7.8 Tech/skills grid with progress bars
- [x] 7.9 Packages/pricing (3 plans, highlighted, “contact for price” option)
- [x] 7.10 FAQ — Alpine accordion + FAQPage JSON-LD
- [x] 7.11 Contact lead form — HTMX POST, honeypot + rate limit, success/error states
- [x] 7.12 Pre-footer CTA improvement (keeps `CTASection`)
- [x] 7.13 Keep featured works / services / testimonials / articles sections working in new flow

### Phase 8 — Footer
- [x] 8.1 Redesigned footer: oversized pixel wordmark, columns, contact, socials, back-to-top
- [x] 8.2 Background rest-state always applies on pre-footer + footer

### Phase 9 — Polish / QA
- [x] 9.1 `seed_home_content` management command with realistic Persian defaults
- [x] 9.2 SEO pass: single H1, meta, JSON-LD, alt texts, heading order
- [x] 9.3 Perf: lazy init, pixelRatio cap, pause off-screen, no layout shift
- [x] 9.4 a11y pass: reduced motion, focus, aria, contrast over the background
- [x] 9.5 Full `manage.py check` + migrations + browser smoke test

## Rules
- One small commit per step, English imperative mood, ≤ ~60 chars. Never broken code.
- `python manage.py check` before every commit; `makemigrations` + `migrate` when models change.
- Rebuild Tailwind (`npm run build`) when classes change. Do not push.
- New sections: model + migration + admin + view/context + partial + seeded Persian content.

## Notes
- `hx-boost` swaps the whole `<body>`, so the background canvas lives in a `hx-preserve`
  wrapper inside `<body>`; htmx keeps it across navigation and the module never re-inits.
- The hero wireframe planet (`engine/scene.js`) is superseded by the page background;
  its loader call is removed but the module is kept (candidate for deletion post-review).
- `CTASection` is global (context processor), so the pre-footer band stays in `base.html`
  and the new home section merely styles around it rather than duplicating the model.
- `AboutStat` already exists for about-page stats; the home stats section gets its own
  model to keep page content independent (prompt §6 asks for per-section settings).
- **Lead form model:** `ContactSubmission` (contact app) has mandatory `project_type` /
  `budget` / `start_time` fields that do not fit a short homepage form, so a dedicated
  `HomeLead` model was added to the `home` app instead of touching the contact app.
- **Alpine + HTMX:** Alpine boots once; after each `htmx:afterSwap` the inline script in
  `base.html` calls `Alpine.initTree(document.body)` so the FAQ accordion keeps working
  after navigation.
- **Section keys ↔ partials:** `seed_home_content` only registers a `HomeSection` row for
  keys listed in `RENDERED_SECTIONS`; a key is added there once its partial exists, so the
  page can never include a missing template.
- **Pinned horizontal scroll:** the horizontal row is opt-in via the `is-horizontal` class
  that `motion.js` sets only when the tween actually runs. Without JS or under
  `prefers-reduced-motion` the process section degrades to a normal stacked grid instead
  of clipped cards.
- **Validation status codes:** the lead endpoint answers 200 for both success and
  validation-error states so htmx swaps the body without extra config; the rate limit and
  honeypot also return the form. Only `GET` answers 405.
