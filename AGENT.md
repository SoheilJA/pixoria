# Pixoria — Master Redesign Log (پیکسوریا)

Persian (RTL) Django agency website. All visitor-facing text: Persian. All code, comments, commits: English.
Source spec: `PIXORIA_AGENT_PROMPT.md`.

---

## Repo Audit

### Stack

- **Backend:** Django 5.2, SQLite (`database/db.sqlite3`, PostgreSQL later — no SQLite-only hacks), django-tinymce 5.0.0, django-unfold (installed but commented out in `INSTALLED_APPS`), Pillow. `manage.py check` passes.
- **Frontend engine:** Django templates (`templates/`, `APP_DIRS` + `templates/` dir). Tailwind CSS v4.3 via standalone CLI (`npm run build` / `npm run watch` → `static/src/input.css` → `static/css/tailwind.css`). GSAP + ScrollTrigger, Three.js, HTMX (`hx-boost="true"` on `<body>`), vanilla JS ES modules. **No Alpine, no Lenis yet.**
- **Admin:** `django.contrib.admin` (unfold disabled). All models registered with Persian `verbose_name`s.
- **Settings:** `config/settings.py` — `STATIC_URL=/public/static/`, `MEDIA_URL=/public/media/`, `LANGUAGE_CODE=fa-ir`, `TIME_ZONE=Asia/Tehran`, context processor `apps.core.context_processors.site_context` (exposes `settings`, `socials`, `cta`, `services_footer`, `stats`).

### Apps & models

- `apps.core` — `SiteSettings` (singleton), `SocialLink`, about-page models (`AboutPageHero`, `AboutStory`, `TeamMember`, `AboutValue`, `AboutStat`, `AboutPre`, `AboutMission`, `AboutProcessStep`, `AboutFaq`), `Proposal` + `ProposalStat/Problem/Service`. Templatetags: `anim_tags.py` (`stagger` filter). Sitemaps: `core/sitemaps.py` (static, portfolio, services, articles).
- `apps.home` — `HeroSection` (singleton), `HeroMarqueeItem`, `FeaturedWorkSection`, `ServicesSection`, `ClientMarqueeItem`, `ManifestoSection`, `CTASection` (used globally), `LatestArticlesSection`.
- `apps.services` — `ServicesPageSection`, `Service` (+ `get_tags_list()`), `ServiceStat`, `ServiceWhyUs` (**icon field is an emoji CharField**), `ServiceDeliverable`, `ServiceProcess`, `ServicePlan` + `ServicePlanFeature`, `ServiceCustomItem`, `ServiceFAQ`, `ServiceTestimonial` (`show_on_home`).
- `apps.portfolio` — `PortfolioPageSection`, `Category`, `Portfolio`, `ProjectStat`.
- `apps.blog` — `Category`, `Tag`, `Author`, `Article` (TinyMCE `HTMLField`, SEO meta fields, auto reading-time), `BlogPageSettings`. TOC built in `blog/utils.py`, HTMX pagination (`load_articles`), admin TinyMCE image upload.
- `apps.contact` — `ContactPageSection`, `ContactInfo`, `ProjectTypeChoice`, `BudgetChoice`, `StartTimeChoice`, `ContactSubmission`. POST handled inline in the view (returns HTML fragments — will be restyled).

### Templates

`base.html` (global shell: preloader with **"P" mark**, header + mega-menu, mobile nav, CTA band, footer), `home/index.html`, `services/{list,detail}.html`, `portfolio/{list,detail}.html`, `blog/{list,detail}.html` + `blog/partials/*`, `core/{about,proposal}.html`, `contact/contact.html`, `404.html`, `registration/login.html`, `admin/login.html`, `includes/_*.html` (older cinematic leftovers), `home/base_cinematic.html`, `_legacy/` (snapshot of previous design — safe to ignore/delete).

### Static assets (already local — no CDN anywhere)

- `static/js/vendor/`: `gsap.min.js`, `ScrollTrigger.min.js`, `lucide.min.js`, `three.module.js`, `htmx.min.js`.
- `static/fonts/`: Vazirmatn (300–600, arabic+latin), Rubik (400–600 + italic), Press Start 2P, Jersey 10 — all woff2, self-hosted via `fonts/font_urls.css`.
- `static/js/`: `main.js` (reveal IO, mobile nav, filters), `core/{utils,motion,reveal,carousel,header}.js`, `engine/scene.js` (hero planet: lime wireframe icosahedron + halo + rings + starfield), `home-motion.js`, `header-motion.js`, `site-reveal.js`, `footer-stars.js`.
- `static/css/`: `tailwind.css` (built), `site.css` (large legacy pixel-art stylesheet, mostly unused by current `base.html`), `blog.css`, `styles.css`.

### Current visual state

- Theme is **light paper (`#f5f4f0`) with near-black ink** and **lime `#c8ff3d`** as the primary accent — the hero and a few sections are already dark (`bg-ink`), the rest is light. Fully-dark conversion needed.
- Header/footer/preloader still use the **"P" box logo**; wordmark text comes from `settings.site_name`.
- Icons: Lucide loaded via `data-lucide` attributes, but many places still use unicode glyphs (`↖ ↓ ★ ✦ ✓`).
- Carousels: one GSAP implementation (`core/carousel.js`) driven by `.carousel` markup, but cards are duplicated inline per page.
- SEO: sitemap exists; **no JSON-LD, no OG/Twitter tags, no canonical, no robots.txt**, titles inconsistent.

### Design decision: primary color

The current project primary is **lime `#c8ff3d`** (`--color-lime` in `input.css`, used by the 3D planet, buttons, accents). Per spec §3 ("use the CURRENT primary green already in the project — do not invent a new hue") we keep lime as the primary accent and derive a full scale + glow + gradient from it.

---

## Task Checklist (simple → complex)

- [x] 1. Repo audit + create `AGENT.md` (architecture summary, checklist, conventions)
- [x] 2. Vendor all libraries locally (GSAP + ScrollTrigger, Three.js + needed addons, Lenis, HTMX, Alpine, Lucide, fonts) into `static/`; remove CDN links; verify the site still works — *all already local; added Lenis; no CDN links exist anywhere in the repo*
- [x] 3. Design tokens + global dark theme using the existing primary green (CSS variables + Tailwind config); fix every light-theme leftover
- [x] 4. Lucide icon system (`{% icon %}` tag) + replace all HTML-entity/emoji icons + icon-name fields in models/admin — *sprite built from local lucide-static v1.49.0 (2121 icons, 716 KB, cached); `{% icon %}` fixed to emit real SVG (was auto-escaped); `ServiceWhyUs.icon` migrated emoji → Lucide names; dead `lucide.min.js` UMD removed*
- [x] 5. Pixel wordmark logo (SVG) + remove the "P" icon everywhere + new favicon set/manifest + admin-replaceable logo/favicon (`SiteSettings`) — *wordmark generated from the self-hosted Vazirmatn 600 by `scripts/build_pixel_wordmark.py`; the "P" is gone from header/footer/preloader/admin/404/contact/about/login; `templates/admin/login.html` was also re-saved (it was corrupted cp1256 with its Persian text lost to literal `?`)*
- [x] 6. Glass & liquid-glass utility classes/components — *`.glass` / `.glass-strong` / `.glass-card` / `.liquid-glass` in `input.css` + `feTurbulence` displacement filter in `base.html` + cursor sheen in `static/js/core/glass.js`; first applied to the services mega-menu*
- [x] 6b. Single shared layout — *`core/about.html`, `contact/contact.html` and `404.html` were fully standalone pages, each carrying its own `<head>`, sidebar rail, mobile header, mobile nav and footer; they now `{% extends 'base.html' %}` so the header, mega-menu, mobile menu, CTA band and footer render from one place. Fixed along the way: dead `static/js/tailwind-main.js` reference and expired `--color-ink-line` var on the 404 page, duplicate `id="content-start"` in `blog/list.html`, dead `.rail-nav` sync block in `main.js`, and a new `{% block extra_head %}` in `base.html` for per-page `<head>` tags (used by the 404 `noindex`)*
- [x] 7. Reusable template components (`templates/components/…`): section header, buttons, cards, badges, etc. — *see "Component library (task 7)" below*
- [x] 8. Reusable **Carousel component** (+ portfolio / testimonial / blog cards) and refactor all existing carousels to use it — *`{% carousel %}…{% endcarousel %}` block tag (`apps/core/templatetags/component_tags.py`) wraps any card partial into `templates/components/carousel.html`; the three home carousels (works / testimonials / latest articles) are the only carousels in the site and all use it. Options moved from JS config to `data-*` attributes, so `initCarousels()` is now one id-agnostic pass that also runs on `htmx:afterSwap`. Arrows are server-rendered Lucide icons (the JS fallback builds the same SVG from the sprite URL it reads off the page); keyboard (←/→/Home/End), `aria-current` dots, reduced-motion autoplay suppression and swap cleanup were added along the way*
- [x] 9. Global motion layer (`data-*`-driven scroll reveals, hover tilt/magnetic/glow, scroll progress, counters) + `prefers-reduced-motion` support — *`static/js/motion.js` is the one motion entry point for every page: reveals (`data-reveal`, migrated from the old `data-aos` markup — 201 attributes across 26 templates), Persian-safe word-split heading reveals (`data-split`), scroll parallax (`data-parallax`), pointer tilt + glare (`data-tilt`), magnetic pull (`data-magnetic`), Persian-locale number counters (`data-counter`) and the `#scroll-progress` header bar. Pointer effects are fine-pointer-only, everything no-ops under reduced motion, and the whole layer re-scans after `htmx:afterSwap`*
- [ ] 10. New header (glass, services mega-menu, scroll behavior) — admin-editable
- [ ] 11. New mobile menu (liquid-glass full-screen overlay, animations, HTMX-aware)
- [ ] 12. New footer
- [ ] 13. SEO fixes (JSON-LD WebSite/Organization/Breadcrumb, titles, OG, canonical, sitemap, robots, HTMX-safe head updates) + `SEO Notes` in `AGENT.md`
- [ ] 14. First-visit preloader (pixel wordmark assembly + real progress + cinematic exit)
- [ ] 15. HTMX page-transition preloader + `PreloaderSettings` admin model (fully editable) + robust HTMX lifecycle re-initialization
- [ ] 16. Hero redesign: planet shifted left, richer planet shader/atmosphere, starfield, parallax, responsive/mobile version
- [ ] 17. Global fixed space canvas + scroll-driven camera journey through planets/stars (subtle, with readability halo/vignette), HTMX-persistent, performance & fallbacks
- [ ] 18. Home page sections rebuilt with varied premium layouts + admin-editable models/inlines + seed data
- [ ] 19. Rebuild/expand **service pages**, each with a unique, service-specific design and data-driven admin-editable sections (models, migrations, admin, seed)
- [ ] 20. Expand the **About page** with many diverse sections (models, admin, seed)
- [ ] 21. Align all remaining pages (portfolio, blog list/detail incl. dark prose, contact, FAQ, 404/500, etc.) with the new design system
- [ ] 22. Extra premium touches I decide to add (scroll-snap moments, cursor follower, easter egg, page-specific space "regions", etc.) — list them in `AGENT.md`
- [ ] 23. Full QA pass: `manage.py check`, migrations, admin editability audit, RTL audit, mobile audit, performance check, console errors, HTMX navigation, reduced-motion, no-JS fallback, no remaining CDN links, no remaining entity icons → final commit `Final QA and polish`

---

## Decisions & Notes

### Design tokens (Task 3) — `static/src/input.css`

| Token | Value | Role |
| --- | --- | --- |
| `--color-night` | `#04070a` | page base + recessed sections |
| `--color-night-soft` | `#070b0f` | alt recessed |
| `--color-paper` | `#0b1116` | raised surface (cards) |
| `--color-paper-soft` | `#0f161c` | raised surface 2 |
| `--color-paper-deep` | `#141d24` | raised surface 3 (inputs/code) |
| `--color-ink` | `#eaf2e8` | headings |
| `--color-ink-soft` | `#b6c2b8` | body text |
| `--color-ink-dim` | `#7f8c82` | meta/captions |
| `--color-mist` / `-soft` / `-dim` | `#c6d1c7` / `#9ba89d` / `#6f7c72` | muted text on dark |
| `--color-line` | `#1e2925` | hairline border |
| `--color-line-strong` | `#2c3a33` | stronger border |
| `--color-lime-50…950` | `#f7ffe6` → `#203004` | primary scale (400 = `#c8ff3d` brand) |
| `--color-lime` / `--color-lime-deep` | `#c8ff3d` / `#a3d130` | aliases for existing markup |
| `--color-lime-soft` / `--color-lime-glow` | `rgba(200,255,61,.10)` / `rgba(200,255,61,.35)` | glass tint / glow |
| radii | `--radius-sm 4` / `md 10` / `lg 14` / `xl 20` / `pill 999` | |
| shadows | `--shadow-card`, `--shadow-glow` | depth + lime glow |
| easing | `--ease-ax`, `--ease-ax-out`, `--ease-spring` | |

Class renames done in templates (mechanical, script-applied): `bg-ink*` → `bg-night*`, `border-ink-line*` → `border-line*`, `text-paper` → `text-ink`, `border-paper` → `border-ink`, `from/to/via-ink` → `…-night`, `bg-white/5` → `bg-ink/5`, `theme-color` → `#04070a`. Body now `bg-night`. Header/megamenu/preloader/carousel/prose restyled for dark in `input.css`. Lime-on-lime hover states corrected to `text-night`.

Verified: all pages 200, computed body bg `rgb(4,7,10)`, zero light surfaces remaining on home/about.

### Lucide icon system (Task 4)

- **Sprite:** `static/icons/lucide.sprite.svg` — one `<symbol id="i-<name>">` per icon, generated from the pinned `lucide-static@1.49.0` (ISC) npm package by `node scripts/build_icon_sprite.js` (regenerate after `npm update lucide-static`). 2121 icons, ~716 KB, served once and browser-cached — a single external `<use>` reference per icon keeps every page body small. A subset sprite is a possible future optimization (only ~25 distinct icons are currently used) but was skipped: the full sprite lets the admin pick any icon without a rebuild step.
- **Template tag:** `{% load icon_tags %}` then `{% icon "zap" class="h-6 w-6 text-lime" size="24" %}` in `apps/core/templatetags/icon_tags.py`. Renders an inline `<svg>` that references the local sprite via `<use href>` (works with `currentColor`, no CDN). **The tag output must be `mark_safe`** — a first attempt returned the raw string, which Django auto-escaped, so every icon rendered as visible literal `<svg …>` text (caught by inspecting the rendered HTML, not by the 200 status).
- **Icon-name validation & admin preview:** `apps/core/icon_utils.py` exposes `available_icons()` (cached parse of the sprite), `validate_icon_name()` (field validator — rejects names missing from the sprite with a Persian message + lucide.dev link) and `DEFAULT_ICON`. `ServiceWhyUsAdmin`-style inlines get a read-only `icon_preview` column rendering the live SVG.
- **`ServiceWhyUs.icon`** was an emoji `CharField(max_length=10)`; now `max_length=64`, `default="sparkles"`, Persian `help_text` with a link to the icon list, and the validator. Existing rows were converted by a data migration (`0004_servicewhyus_emoji_to_lucide`): ⚡→`zap`, 📱→`smartphone`, 🎨→`palette`, 🔒→`shield-check` (+ a 40-entry fallback map for other common emoji).
- **Cleanup:** the unused 444 KB `lucide.min.js` UMD bundle was removed (the site uses the sprite, not the runtime JS API); the last entity/emoji glyphs in live templates (`✕`, `↗`, `←`, `🔗`, `✓`) were replaced with `{% icon %}`.

### Pixel wordmark & brand (Task 5)

- **Generator:** `scripts/build_pixel_wordmark.py` rasterizes «پیکسوریا» with the self-hosted **Vazirmatn 600** (OFL) via Pillow, pixelates the *ink* onto a 14-row grid and emits crisp square pixels. Without libraqm, Pillow cannot shape/join Arabic, so letters are laid out individually in visual order — isolated letterforms are the intended pixel-font look. Re-run it after touching the font/text/accent.
- **Assets** (all in `static/brand/`): `wordmark-full.svg` (ink via `currentColor` + lime accent on the «ک»), `wordmark-mono.svg` (single colour, tinted by CSS), `mark-compact.svg` (pixel «پ»), `favicon-{16,32,48,192,512}.png`, `apple-touch-icon.png` (180), multi-size `favicon.ico`, `favicon.svg`, `site.webmanifest` (RTL, `lang: fa`, lime-on-night).
- **Template tag:** `{% load brand_tags %}` → `{% pixel_wordmark "full" class="h-6 text-ink" %}` inlines the SVG (needed for the rect-level animation). Variants: `full` / `mono` / `compact`.
- **Admin-replaceable:** `SiteSettings.logo` / `.favicon` / `.apple_touch_icon` (`FileField`, `upload_to="brand/"`, blank allowed). Templates fall back to the generated assets when blank, so the pixel wordmark is the default and uploads override it.
- **Animation:** `.wordmark rect` gets a staggered `pixel-in` keyframe — on `.wordmark-link` hover and once when the preloader activates (`static/js/core/wordmark.js`, `htmx:afterSwap`-aware, skipped under `prefers-reduced-motion`).
- **Preloader** panels switched from lime to `--color-night` so the white+lime wordmark stays legible on them (task 14 will rebuild the preloader fully).

### Glass system (Task 6)

| Class | Blur | Surface | Use for |
| --- | --- | --- | --- |
| `.glass` | 14px | paper 58% translucent | base panels, chips, badges |
| `.glass-strong` | 26px | paper 80% translucent | menus, overlays, modals (small text) |
| `.glass-card` | 16px | paper 58% + lime glow on hover | cards |
| `.liquid-glass` | 26px | paper 66% + refraction + cursor sheen | hero surfaces, buttons, feature cards |

- All four share a translucent top-lit gradient, a 1px inner highlight on the **top-left** edge (`inset 1px 1px 0 rgba(255,255,255,.10)`), an inner bottom-right shadow and a soft outer shadow. `.glass-card:hover` adds a lime border + `--color-lime-glow`.
- **Liquid glass** = `feTurbulence` + `feDisplacementMap` filter `#pixoria-glass` (defined inline in `base.html`, ~200 B) applied to a `::before` specular streak, plus a `::after` radial sheen tracking the pointer through `--gx/--gy` (set by `static/js/core/glass.js`, `pointermove`, passive). Both pseudos sit at `z-index: -1` behind the content, so **pair `.liquid-glass` with a `relative z-10` content wrapper**.
- **Fallbacks:** `@supports not (backdrop-filter)` swaps to a solid `--color-paper` background; an unresolved `filter: url(#…)` is dropped by the browser so liquid glass degrades to frosted glass on the standalone pages that don't carry the filter def. The cursor sheen is disabled on `(hover: none)` and `prefers-reduced-motion`, and transitions are killed under reduced motion.
- **Perf:** the displacement filter is only on `.liquid-glass` elements, never on full-screen or huge areas (the mobile menu keeps a solid `--color-night` until task 11 rebuilds it).

### Component library (task 7)

`templates/components/` — plain Django partials, `{% include … with … %}`, no custom tags beyond the existing `{% icon %}`. Props are documented in a comment at the top of each file and summarised in `templates/components/README.md`.

| Component | Replaces | Consumed by |
| --- | --- | --- |
| `page_hero.html` | the six near-identical inner-page hero blocks (padding, breadcrumb, title rhythm differed per page) | about, contact, services list, portfolio list, blog list |
| `breadcrumb.html` | the five inline `خانه › …` trails | page_hero, blog detail hero, portfolio/service detail heroes |
| `section_header.html` | the ~12 duplicated `eyebrow + h2 [+ subtitle]` header blocks | home (4 sections), about (4), services detail (5) |
| `button.html` | raw `.btn .btn-*` anchors/buttons (21 call sites) | home hero, blog list, services detail, blog sidebar CTA |
| `badge.html` | the three ad-hoc pill variants (solid lime / bordered / soft) | service tags, portfolio categories, blog category + tags |
| `cta_banner.html` | the pre-footer CTA band that was inline in `base.html` | base.html (once, for every page) |
| `cards/blog_card.html` | two inline article-card markups (home carousel + blog grid) | home latest-articles carousel, `blog/partials/article_cards.html` |
| `cards/portfolio_card.html` | the inline featured-work card | home works carousel |
| `cards/testimonial_card.html` | two inline testimonial cards (home + services detail) | both |
| `cards/service_card.html` | the inline bento service tile | home services grid |

Supporting code: `apps/core/context_utils.py` adds `crumbs(*items)` so views build breadcrumb trails as `("خانه", "home:home"), ("درباره ما", None)` tuples (the last entry is the current page). Every page view now passes `crumbs`; `Category.filter_url` was added so portfolio category pills can ask the model for their filtered archive URL instead of concatenating it in the template.

### Carousel component (task 8)

One carousel for the whole site: a `{% carousel %}…{% endcarousel %}` block tag (`apps/core/templatetags/component_tags.py`) renders `templates/components/carousel.html` and feeds the wrapped markup into the partial's `content` slot, so the track is filled with any card partial at the call site. The home page's three carousels (featured works, testimonials, latest articles) use it.

- **Tag implementation detail:** the partial is rendered through the *engine-level* `base.Template` (`get_template(...).template`), reached the same way `IncludeNode` does it. `backends.django.Template.render()` only accepts a plain dict — passing the live `Context` raises `TypeError: context must be a dict rather than RequestContext`, which is invisible until the tag is actually used on a page with a `RequestContext`.
- **Prop isolation:** the wrapped markup is rendered in the untouched outer context *before* the carousel props are pushed, so a wrapper prop like `class="mt-16"` never leaks into the card partials placed inside the block (it silently landed on the first card's `<article>` otherwise).
- **Booleans have defaults in the tag, not the template:** `arrows`/`dots` default to `true`, but a `{% if arrows %}` in the partial is falsy when the caller omits the kwarg (a missing variable resolves to `string_if_invalid`), so the tag `setdefault`s them. Numeric props (`per_view`, `gap`, `interval`) fall back through `|default` in the template.
- **Options moved to `data-*`:** `static/js/core/carousel.js` used to carry a hardcoded `byId("works-carousel", { perView: 4 })` list. Every option now lives on the wrapper (`data-per-view`, `data-gap`, `data-autoplay`, `data-interval`, `data-show-arrows`, `data-show-dots`), so `initCarousels()` is one generic pass over `.carousel` that also covers markup arriving in an HTMX swap. `main.js` re-runs it on `htmx:afterSwap`, and swapped-out carousels are destroyed (interval + resize listener) via a small instance registry keyed on `isConnected`.
- **Arrows are real Lucide icons:** the template renders them with `{% icon %}`. The JS fallback (for a bare `.carousel` whose markup came from elsewhere) builds the same inline `<svg><use>` string, reading the sprite URL off the first icon already on the page so no static path is hardcoded. The old injected buttons used the `→`/`←` glyphs, which regressed task 4's no-entity-icons rule.
- **RTL:** the track starts at the right edge, so advancing is a *positive* `translateX`; the previous button therefore sits on the right and points right (`arrow-right`), the next one on the left (`arrow-left`). Keyboard mirrors this — `ArrowLeft` advances, `ArrowRight` goes back (matching the swipe handler); `Home`/`End` jump to the ends. Arrow keys only act when the focus is on the carousel chrome (nav/dots/track), so links inside slides keep normal behaviour.
- **A11y/perf:** `role="list"` on the track, `role="group"` on the dot strip with Persian `aria-label`s, `aria-current` on the active dot, autoplay suppressed under `prefers-reduced-motion` and skipped while the tab is hidden, hover/touch still pauses autoplay.

**Verified:** `manage.py check` clean; home renders exactly three `.carousel` wrappers, each with one nav (two Lucide arrow buttons) and one dot strip; all nine page routes (incl. service/portfolio/article details) return 200; `node --input-type=module --check` passes on the JS.

### Global motion layer (task 9)

`static/js/motion.js` — one entry point, loaded once in `base.html` (it replaced `static/js/site-reveal.js`) and re-scanned on `htmx:afterSwap`. Everything is `data-*` driven so templates stay declarative:

| Attribute | Effect |
| --- | --- |
| `data-reveal="up\|down\|left\|right\|fade\|blur"` | scroll reveal, once (`data-reveal-delay` / `data-reveal-duration` in ms) |
| `data-split` | word-by-word heading reveal — split on whitespace only, never per letter, so Arabic-script joining stays intact |
| `data-parallax="0.2"` | scroll-linked vertical drift over the viewport height (negative inverts); decorative layers only |
| `data-tilt` (+ `data-tilt-max`) | pointer 3D tilt + specular glare pseudo-element; writes only `--rx/--ry/--gx/--gy` |
| `data-magnetic="12"` | pointer magnetic pull on buttons, elastic release |
| `data-counter="1234"` | count-up on scroll; `data-counter-decimals`, `-prefix`, `-suffix`, `-locale="en"` (defaults to Persian digits via `fa-IR`) |
| `#scroll-progress` | brand-green scroll progress bar inside the header (`transform-origin: right` — the RTL page starts at the right edge) |

Behaviour notes:

- **Reveal system, unified:** the old `data-aos*` markup is gone from every template (201 attributes across 26 files renamed, plus the dead AOS `data-aos-anchor-placement` attribute removed). `core/reveal.js` still *reads* `data-aos*` as a legacy alias, so a stray attribute elsewhere degrades to the new system instead of silently doing nothing. Card siblings share one staggered group; `.rv` class support and the 4-second safety net (show anything still hidden) are kept.
- **`data-tilt` composes with `data-reveal`:** the tilt writes CSS custom properties, and `core/reveal.js` adds `clearProps: "transform"` when the revealed element also carries `data-tilt`, so GSAP's inline transform steps aside once the reveal lands. `data-magnetic` still owns the transform, so it must not be combined with `data-reveal` (documented in the module header).
- **Reduced motion / touch:** under `prefers-reduced-motion` no effect animates and counters jump to their final value; tilt and magnetic are skipped entirely on coarse pointers (`(hover: hover) and (pointer: fine)`).
- **HTMX hygiene:** after a swap, stale ScrollTriggers whose trigger element left the DOM are killed before the new content is scanned, so page-to-page navigation does not pile up tweens.
- **Renamed `core/motion.js` → `core/home-motion.js`** (home hero only) so the global layer could take the `motion.js` name; the home loader and its Persian comments were translated at the same time.

**Verified:** all six main routes return 200 with zero `data-aos` left in the rendered HTML, the `#scroll-progress` element and `motion.js` are present on every page, `npm run build` succeeds and the new component classes are in `static/css/tailwind.css`, and `node --input-type=module --check` passes on every touched JS file.

**Verified:** all nine page routes (home, about, contact, services list/detail, portfolio list/detail, blog list/detail) return 200; each renders exactly one header, one breadcrumb trail, one CTA band and one footer; the contact form still POSTs and returns the Persian success fragment; `manage.py check` clean.

**Gotcha worth remembering:** Django's template lexer (`tag_re` in `django/template/base.py`) is **not** compiled with `re.DOTALL`, so a `{# … #}` comment is only recognised when it fits on **one line**. A multi-line doc comment is never treated as a comment — its `{#` and everything after it lands in the output as literal text (and any `<a>`/`<button>` mentioned inside is then swallowed by the browser as markup, so the text looks mangled on the page). Component prop docs therefore use **one `{# … #}` per line**, and no comment may contain `{%`, `{{` or `#}` — those are still parsed/tag-delimiters inside a single-line comment, which is how a self-referencing `{% include %}` example once made a file include itself and die with `RecursionError`. A repo-wide scan for multi-line `{#` is part of the QA checklist (task 23).

Before this pass, three page templates were entirely standalone documents instead of extending the base shell:

- `templates/core/about.html`, `templates/contact/contact.html`, `templates/404.html` — each had its own `<head>`, a desktop **sidebar rail** (`aside.rail-nav`), a mobile-only `<header class="mobile-header">`, a duplicate `#mobile-nav`, and its own `<footer>`. The header/footer/CTA markup therefore existed in up to four copies that drifted apart.
- They now `{% extends 'base.html' %}` and only override `title`, `description` (and `extra_head` for the 404 `noindex`). The sidebar rail layout was dropped on purpose — it was the only place in the site using it, so it broke the "one header, one footer, one rhythm" rule in §3. The about page keeps its `pre` (manifesto) section, which sits above the global CTA band.
- `templates/base.html` gained `{% block extra_head %}` next to `extra_css` for per-page `<head>` tags.
- Cleanup that fell out of it: the 404 page referenced a non-existent `static/js/tailwind-main.js` and the renamed CSS var `--color-ink-line` (→ `--color-line-strong`); `blog/list.html` duplicated the base `<main id="content-start">` id on a section; `static/js/main.js` had a `.rail-nav` → `.mobile-nav` active-link sync that no longer has a source element (base.html's own `syncActiveNav()` already handles active state after load and after every HTMX swap).

Verified: `manage.py check` clean; home/about/contact return 200 and render exactly one header, one mobile nav, one CTA band, one footer; 404 renders the themed page (visible only with `DEBUG=False` — under `DEBUG=True` Django answers with its technical page, which is expected); the contact form still POSTs and returns the Persian success fragment; direct URLs work as full standalone pages so crawling/HTMX are both safe.


- **Primary accent:** lime `#c8ff3d` (existing). Scale derived from it: 50 `#f6ffe0` … 950 `#3d5a00`, glow `rgba(200,255,61,…)`, gradient lime → `#d8ff7a` (cyan-shifted lighter).
- **JS stack:** vanilla ES modules + GSAP/ScrollTrigger + Three.js + HTMX. **Alpine.js intentionally not added** (vanilla covers the interaction layer; one less library). Lenis added locally in Task 2 for smooth scroll.
- **Fonts:** keep self-hosted Vazirmatn (body) + Rubik (display) — already good Persian coverage.
- **Commits:** one short English imperative commit per checklist item.

### Library versions (local, pinned)

| Library | Version | Path |
| --- | --- | --- |
| GSAP + ScrollTrigger | 3.12.5 | `static/js/vendor/gsap.min.js`, `ScrollTrigger.min.js` |
| Three.js | r160 | `static/js/vendor/three.module.js` |
| HTMX | 1.9.10 | `static/js/htmx.min.js` |
| Lucide | full icon bundle (UMD) | `static/js/vendor/lucide.min.js` |
| Lenis | 1.1.13 | `static/js/vendor/lenis.mjs` |
| Vazirmatn / Rubik | self-hosted woff2 | `static/fonts/` |

**CDN audit:** zero external `http(s)://` script/style/font links in templates, JS, CSS or Python. Every library is served from `static/`. Alpine.js intentionally not added (vanilla ES modules cover all interactions).

## Known Issues / Follow-ups

- `static/css/site.css` is a 2.2k-line legacy stylesheet from a previous pixel-art design; most of it is dead. Will be trimmed/removed as the new system lands.
- **Dead template trees deleted** (unreferenced by any view, recoverable from git): `templates/_legacy/`, `templates/includes/_*.html`, `templates/home/base_cinematic.html`, and the unused 444 KB `static/js/vendor/lucide.min.js` UMD bundle.
- **Persian code comments:** the previous pass wrote Persian comments inside `static/js/**/*.js`. `core/reveal.js`, `core/carousel.js` and `core/home-motion.js` are now English (done while task 8/9 touched them); `js/footer-stars.js`, `js/header-motion.js`, `core/header.js` and `engine/{scene,footer-stars}.js` still carry Persian comments — to be translated in a follow-up commit.
- `django-unfold` is in `requirements.txt` but commented out — admin stays stock Django for now.
