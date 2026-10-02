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
- [ ] 5. Pixel wordmark logo (SVG) + remove the "P" icon everywhere + new favicon set/manifest + admin-replaceable logo/favicon (`SiteSettings`)
- [ ] 6. Glass & liquid-glass utility classes/components
- [ ] 7. Reusable template components (`templates/components/…`): section header, buttons, cards, badges, etc.
- [ ] 8. Reusable **Carousel component** (+ portfolio / testimonial / blog cards) and refactor all existing carousels to use it
- [ ] 9. Global motion layer (`data-*`-driven scroll reveals, hover tilt/magnetic/glow, scroll progress, counters) + `prefers-reduced-motion` support
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
- **Dead template trees still on disk, unreferenced by any view or template:** `templates/_legacy/` (old-design snapshot), `templates/includes/_*.html` + `templates/home/base_cinematic.html` (cinematic leftovers, only referenced by each other). They still contain the old entity/glyph icons (`←`, `★`, `✕`, `▲`) — safe to delete (recoverable from git), pending a delete approval.
- **Persian code comments:** the previous pass wrote Persian comments inside `static/js/**/*.js` (11 files). Per the project rules comments must be English — to be translated in a follow-up commit.
- `django-unfold` is in `requirements.txt` but commented out — admin stays stock Django for now.
