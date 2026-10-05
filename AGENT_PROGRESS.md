# Pixoria — V2 Frontend Migration Progress

Migrating the static `new/` design (gold/cream/ink palette) into the Django
backend, replacing the old lime/dark-space frontend.

## Rules for resuming

1. Read this file fully. Do NOT re-plan, do NOT redo any task marked `[x]`.
2. Find the first unchecked task. Run `git status` and `git log --oneline -15`
   to see whether it was partially done; finish it from where it stopped.
3. After each task: tick `[x]`, update `## Current status`, run
   `python manage.py check` (+ makemigrations/migrate when models changed),
   then ONE short English commit including this file.
4. Never tick a task that is not fully done and verified.

## Project facts discovered

### Stack

- Django 5.2, SQLite (`database/db.sqlite3`), Python 3.13 in `venv/`.
- Tailwind v4 CLI build: `npm run build` → `static/src/input.css` →
  `static/css/tailwind.css` (gitignored output, must be rebuilt after token
  changes).
- Templates: root `templates/` dir (set via `TEMPLATES[0]["DIRS"]`), app dirs
  also scanned. `templates/base.html` is the layout single source of truth.
- Context processor `apps.core.context_processors.site_context` exposes:
  `settings` (SiteSettings), `socials` (SocialLink), `cta` (CTASection),
  `services_footer` (Service[:5]), `stats` (AboutStat), `header_settings`
  (HeaderSettings), `nav_items` (NavItem active).
- `python manage.py check` currently passes.

### Apps & URL names

- `apps.home`: `home:home` (`/`), `home:lead` (HTMX lead POST).
- `apps.portfolio`: `portfolio:list`, `portfolio:detail(slug)`.
- `apps.services`: `services:list`, `services:detail(slug)`.
- `apps.core`: `core:about` (`/about/`); root-level `proposal(slug)`.
- `apps.contact`: `contact:contact` (`/contact/`).
- `apps.blog`: `blog:list`, `blog:load`, `blog:detail(slug)`,
  `blog:tinymce-image-upload`.
- `config/urls.py`: `handler404 = "config.views.custom_404"` (renders
  `templates/404.html`). No handler500.
- Sitemap at `/sitemap.xml` (static, portfolio, services, blog).

### Existing models (reuse, do not duplicate)

- `core.SiteSettings` (singleton): site_name, site_description,
  footer_description, email, phone, address, established_year, status, logo,
  favicon, apple_touch_icon.
- `core.SocialLink`: label, name, url, order.
- `home.HeaderSettings` (singleton): cta_text, cta_url, show_cta.
- `home.NavItem`: title, url (URL name or path), order, is_active.
- `home.CTASection` (singleton): title, description, email, phone.
- `home.HomeSection`: key/order/is_active registry driving section rendering;
  `home/index.html` loops `{% include "home/sections/_"|add:key|add:".html" %}`.
- `home.HeroSection` (singleton), `home.HeroMarqueeItem`.
- `home.ClientMarqueeItem` (name, order) — for the clients/trusted marquee.
- `home.WhySection` + `home.WhyFeature` (icon, title, description,
  size=small/wide/tall).
- `home.ProcessSection` + `home.ProcessStep` (title, description).
- `home.StatsSection` + `home.StatItem` (value Decimal, prefix, suffix,
  label, description).
- `home.TechSection` + `home.TechSkill` (name, level, category).
- `home.FaqSection` + `home.FaqItem` (question, answer).
- `home.HomeLead` (name, phone, service FK, message, status).
- `services.Service` (title, slug, excerpt, description, tags csv, featured),
  plus ServiceStat/WhyUs/Deliverable/Process/Plan/CustomItem/FAQ/Testimonial.
- `portfolio.Portfolio` (title, slug, excerpt, description, image,
  categories M2M, client_name, year, service_type, client_url, challenge,
  solution, featured, order) + `ProjectStat`; `portfolio.Category`
  (name, slug, order).
- `blog.Article` (title, slug, category, tags, author, cover_image, excerpt,
  content HTMLField, reading_time auto, status, published_at, meta_*).
- `contact.ContactPageSection`, `contact.ContactInfo` (office_title,
  office_address, phone, working_hours, email_project/press/career, tagline),
  `ContactSubmission`, choice models (ProjectType/Budget/StartTime).
- `core.AboutPageHero`, `AboutStory`, `AboutMission`, `AboutValue`,
  `AboutStat`, `AboutProcessStep`, `AboutFaq`, `AboutPre`, `TeamMember`.

### The new design (`new/`)

- Pages: `index.html` (home), `about.html`, `contact.html`,
  `services/{web-design,programming,graphic-design,logo-design}.html`.
- Tokens (`new/assets/css/input.css` @theme): `ink #0a0a0c`, `ink2 #121214`,
  `ink3 #060607`, `cream #f5f3ee`, `cream2 #efece5`, `paper #1e1b15`,
  `coy #5c5647`, `gold #c9a15a`, `gold-light #e8c47a`, `gold-dark #8f6b2c`,
  `royal #2e63ff`; fonts Vazirmatn (fa) + Space Grotesk (latin, `--font-latin`).
- ~204 custom CSS classes in `input.css` (glass, tile, btn, svc-card,
  why-card, process-step, marquee, faq-item, stat-card, blog-card, divider,
  eyebrow, aurora-blob, grid-bg, pixel-bg, shard, orb, …).
- CDN usage to eliminate: `cdn.tailwindcss.com` (about/contact/services),
  Vazirmatn font-face CSS + Space Grotesk from Google Fonts, gsap /
  ScrollTrigger / lenis / lucide UMD from jsdelivr, three + addons from
  jsdelivr import map.
- Home page section order (`new/index.html`): hero (Three.js starfield +
  crystal planet, `#hero-3d`/`#hero-canvas`, CSS `#hero-fallback`) → about →
  services (4 bespoke cards) → trusted (brand marquee) → portfolio (filterable
  grid, `#pf-*`) → why (6 cards) → process (GPS SVG timeline + 5 steps) →
  testimonials (slider `#t-*` + video card `#v-*` + audio card `#a-*`) →
  tech (two marquee rows of chips) → stats (4 counters) → blog (3 cards) →
  faq (accordion) → cta (pill buttons) → footer `#contact` (4 columns,
  enamad/samandehi cards, toast `#toast`).
- Header: glass pill nav, services mega-menu, mobile overlay menu, CTA
  «مشاوره رایگان». Footer: brand + contact list + quick links + services
  links + enamad cards + copyright.
- Interaction API (all in one inline `<script>` at end of body): Lenis smooth
  scroll, `data-reveal` (up/right/left/scale) + `data-delay`, `data-counter`
  (+prefix/suffix, fa-IR digits), `data-magnetic`, `data-tilt` (+glare),
  `data-float`, scroll progress bar, scroll-spy nav, FAQ accordion,
  portfolio filter, testimonial slider, video/audio players.

### Old home vs new home — section diff

| Old (HomeSection keys) | New `index.html` | Mapping / decision |
|---|---|---|
| hero | hero (3D + fallback) | `HeroSection` extended |
| clients | trusted (brand plates) | `ClientMarqueeItem` extended (mark + accent) |
| works | portfolio grid + filters | `Portfolio` + `portfolio.Category` (filter key) |
| services | services (4 bespoke cards) | `Service` extended (visual kind, chips) |
| process | process (GPS timeline) | `ProcessStep` extended (icon) |
| why | why (6 cards) | `WhyFeature` reused (icon + index styling) |
| stats | stats (4 counters) | `StatItem` extended (icon) |
| tech | tech (marquee chips) | `TechSkill` extended (icon, marquee render) |
| packages | — | NOT in new home; keep model, drop from home rendering |
| testimonials | testimonials (text/video/audio) | `ServiceTestimonial` extended (kind + media) |
| faq | faq | `FaqItem` reused |
| contact (lead form) | — (footer holds contact) | keep lead form; render as home section |
| manifesto | — | not in new design; keep model, drop from home |
| articles | blog (3 cards) | `Article` reused |
| — | about (short intro) | NEW `HomeAboutSection` model |
| — | cta (pill buttons) | `CTASection` reworked into new pill style |

Pending pages (no new design in `new/`): blog list/detail, portfolio
list/detail, services list/detail, proposal, login. These keep working with
the old templates until restyled; they already extend `base.html`, so the new
base restyles them automatically. Service detail pages exist in `new/services/`
but are out of scope for this migration order (home/about/contact/404 only).

## Decisions log

- **D1 — Full replacement, no coexistence (user directive).**
  `static/src/input.css` is fully replaced by the V2 design (tokens + all
  custom CSS from `new/assets/css/input.css`). Nothing of the old frontend
  survives: old tokens (`--color-night`, `--color-lime`, …), old custom CSS
  (`.liquid-glass`, `.preloader`, `.bg-shell`, …), old JS
  (`main.js`, `motion.js`, `cursor.js`, `pixoria-bg/`, `engine/`, …) and old
  Rubik/pixel font files are all deleted in the cleanup phase. Interim
  consequence: pages whose templates are not converted yet render unstyled
  until they are replaced — that is expected and part of the migration.
  Pages with no new design (`blog/*`, `portfolio/*`, `services/*`, `login`)
  get minimal placeholders extending the new `base.html` (see §8 of the
  prompt) so no URL is broken.
- **D2 — Colored heading marker.** Template filter `highlight` in
  `apps/core/templatetags/highlight_tags.py`: escapes text, converts
  `[[word]]` → `<span class="text-goldgrad">word</span>`; use
  `{{ x|highlight:"dark" }}` for the light-background variant
  (`text-goldgrad-dark`). Multiple markers per heading supported. Every
  heading field gets Persian `help_text`: «کلمه‌ای که باید رنگی شود را داخل
  [[ ]] بنویسید».
- **D3 — Icons stay local.** The new design's `<i data-lucide="…">` + CDN
  UMD is replaced by the existing local Lucide sprite + `{% icon %}` tag
  (`apps/core/templatetags/icon_tags.py`, sprite at
  `static/icons/lucide.sprite.svg`, rebuilt by
  `scripts/build_icon_sprite.js`). No lucide JS at all.
- **D4 — Vendor JS already local.** `static/js/vendor/` already holds
  gsap.min.js, ScrollTrigger.min.js, lenis.mjs, three.module.js. The new
  inline page script moves to `static/js/pixoria.js` (defer, end of body).
- **D5 — Fonts self-hosted.** Vazirmatn woff2 already in `static/fonts/`.
  Space Grotesk woff2 (300/400/500) must be downloaded into
  `static/fonts/` and registered in `static/fonts/font_urls.css` with
  `font-display: swap`. No Google Fonts / jsdelivr font CSS.
- **D6 — Section system kept.** The home page keeps rendering sections from
  `HomeSection` order/is_active, so the admin still controls order. New keys
  added: `about`, `trusted`, `portfolio`, `blog`. Keys without a new-design
  partial (`packages`, `manifesto`) are removed from RENDERED_SECTIONS and
  their models stay untouched.
- **D7 — Header/footer/CTA in base.html via includes.**
  `templates/partials/_header.html`, `_footer.html`, `_cta.html` included by
  `base.html`; all content DB-driven (NavItem, HeaderSettings, SiteSettings,
  SocialLink, CTASection, Service list for mega-menu/footer).
- **D8 — 3D performance rules.** The hero Three.js scene is moved to a
  standalone module `static/js/hero-scene.js` loaded with `type="module"` +
  IntersectionObserver gate (init only when `#hero-3d` is near viewport),
  `requestIdleCallback`/`load` deferral, `pixelRatio ≤ 2`, pause on
  off-screen/hidden tab, dispose on teardown, `prefers-reduced-motion`
  skip, CSS fallback `#hero-fallback` poster.
- **D9 — Mega-menu from DB.** The services mega-menu items are generated
  from `Service` objects (icon, title, excerpt, url) instead of a new model;
  a `SiteSettings`-level banner line is added for the promo banner text.
- **D10 — Mega-menu wiring (T06).** The mega menu is attached to whichever
  `NavItem` resolves to `services:list` (`{% url 'services:list' as
  services_url %}` + `{% nav_url item.url as item_url %}` string compare), so
  the admin still reorders/renames nav items freely. Service cards come from
  the existing `services_footer` context (≤5). On mobile, services render as
  a nested sub-list under the same nav item (`.m-link` smaller style).
- **D11 — Persian digits.** Filter `fa_digits` in
  `apps/core/templatetags/fa_digits.py` translates latin digit runs to
  fa-IR (`{{ forloop.counter|stringformat:"02d"|fa_digits }}` → «۰۱»). Use
  it anywhere a latin-digit source is rendered (ordinals, counters, phones).
- **D12 — Mega-banner copy.** `SiteSettings.mega_title` (runs through the
  `highlight` filter, so `[[ ]]` markers work), `.mega_description`,
  `.mega_cta_text` (default «مشاهده همه خدمات», links to `services:list`);
  the banner block is skipped entirely when `mega_title` is empty.
- **D13 — Footer partial wiring (T07).** Brand column: logo/wordmark +
  `tagline` + `footer_description` + «از سال {established_year}», contact list
  from `phone`/`phone_secondary`/`email`/`website`, socials as `.soc` buttons
  (`SocialLink.icon`). Link columns come from `footer_groups`
  (`FooterLinkGroup` → `FooterLink`, active-only, prefetched by the context
  processor), services from `services_footer`, trust cards from the
  `trust_*` SiteSettings fields. Every column is `{% if %}`-guarded, so an
  empty DB renders a valid (sparse) footer. The footer owns `id="contact"` —
  the home lead-form section (T24) must use a different anchor id.
- **D14 — CTA partial wiring (T08).** `CTASection.eyebrow` added (small gold
  line above the title); `title` runs through `highlight` and its help_text
  explains the `[[ ]]` marker. Primary pill → `contact:contact` (label
  «مشاوره رایگان» kept as a constant UI label), secondary pill → `tel:` with
  `phone` (`.fa-num`), plus a discreet `mailto:` link when `email` is set so
  the existing email field is still rendered. The whole section is wrapped in
  `{% if cta %}`. The design's cream top-divider was dropped: the partial is
  included above the footer on every page, and the wave only reads correctly
  against a light preceding section.
- **GOTCHA — template comments.** Django's lexer regex
  (`{%.*?%}|{{.*?}}|{#.*?#}`, no DOTALL) means `{# … #}` only comments a
  SINGLE line; a multi-line `{#` block leaks its text into the rendered HTML.
  Use `{% comment %}…{% endcomment %}` for multi-line notes in templates.
- **D15 — base.html v2 layout (T09).** Composes
  `partials/_header.html` → `<main id="main">` (content block →
  `partials/_cta.html` → `afterPrefooter` block) → `partials/_footer.html`,
  plus the skip link, `#scroll-progress` bar, `.grain` overlay and `#toast`
  (role=status, local `check` icon). Assets, all local and deferred:
  `js/vendor/gsap.min.js` + `js/vendor/ScrollTrigger.min.js` (defer, globals),
  `js/pixoria.js` (module — T10), `js/hero-scene.js` (module — T11),
  `js/htmx.min.js` (defer, for the lead/contact forms). Dropped from v1:
  Alpine (v2 FAQ/menu are plain JS in pixoria.js), `hx-boost` on `<body>`
  (plain multi-page navigation; htmx stays only for form posts), the
  `bg-shell`/preloader/`pixoria-glass` SVG scaffolding, `{{ preset }}`
  bg-config json_script and the old inline nav-sync script (pixoria.js owns
  scroll-spy now). `<main>` has NO top padding — the fixed glass header is
  designed to overlay full-bleed heroes, and inner pages give their own hero
  top padding (old `components/page_hero.html` already has
  `pt-[clamp(64px,9vw,130px)]`).
- **D16 — pixoria.js (T10).** ES module; `import Lenis from
  "./vendor/lenis.mjs"` (that file has a `default` export), GSAP +
  ScrollTrigger consumed as globals from the defer scripts in base.html. All
  features degrade without GSAP / with reduced motion / on touch. Differences
  from the `new/` inline script: (a) no `lucide.createIcons()` (local sprite,
  D3); (b) nav "active" state is **path-based** (`location.pathname` vs each
  `.nav-link` href), re-synced on `htmx:pushedIntoHistory`/`afterSettle` —
  the v1 section scroll-spy is dropped because nav items are real page URLs;
  (c) the hero WebGL-fallback timer lives in hero-scene.js (T11) which owns
  the `window.__hero3d` flag; (d) toast is also exposed as
  `window.pixoriaToast(msg)` and announced automatically after
  `htmx:afterSettle` when the swapped content contains a `[data-toast="…"]`
  element — the lead form success template (T24) and contact form (T30) use
  that attribute; (e) Esc closes the mobile menu; sliders/media cards guard
  against missing sub-elements so partials can render without them.
- **D17 — hero-scene.js (T11).** Faithful port of the `new/` hero module
  (PMREM-lit env, 3 star layers, crystal planet, rings, moons, scroll-driven
  `travel`) wrapped in the D8 rules: renderer is only built after `load` +
  `requestIdleCallback` AND an IntersectionObserver gate (rootMargin 200px);
  `pixelRatio ≤ 2`; the loop is *paused* (`setAnimationLoop(null)`) rather
  than skipped when the hero leaves the viewport or the tab is hidden, and
  resumed on return; full disposal (geometries, materials, textures, PMREM,
  renderer) on `pagehide`; reduced-motion renders nothing and shows the CSS
  poster; any exception or a 3.5s boot timeout falls back to
  `#hero-fallback`. Owns the `window.__hero3d` flag and calls
  `ScrollTrigger.refresh()` after its late-added triggers are created.

## Tasks

### Phase 0 — Foundation

- [x] T01 — Replace Tailwind source with V2 design tokens and custom CSS |
  files: `static/src/input.css` | commit: "feat(css): replace design tokens with v2 gold theme"
- [x] T02 — Self-host Space Grotesk woff2 and register font faces |
  files: `static/fonts/*`, `static/fonts/font_urls.css` | commit: "feat(fonts): self-host space grotesk woff2"
- [x] T03 — Add `highlight` template filter for `[[ ]]` colored words |
  files: `apps/core/templatetags/highlight_tags.py` | commit: "feat(templatetags): add highlight filter for colored headings"
- [x] T04 — Extend site chrome models (SiteSettings footer/contact fields,
  SocialLink icon) + migration + admin |
  files: `apps/core/models.py`, `apps/core/migrations/`, `apps/core/admin.py` | commit: "feat(core): extend site settings and social link models"
- [x] T05 — Rebuild local Lucide sprite to cover every icon used in `new/` |
  files: `static/icons/lucide.sprite.svg`, `scripts/build_icon_sprite.js` | commit: "chore(icons): rebuild lucide sprite for v2 design"

### Phase 1 — base.html (header / footer / CTA)

- [x] T06 — Create header partial (glass nav, DB mega-menu, mobile overlay) |
  files: `templates/partials/_header.html`, `apps/core/models.py`,
  `apps/core/migrations/0008_*`, `apps/core/admin.py`,
  `apps/core/templatetags/fa_digits.py` | commit: "feat(base): add v2 header partial with db mega menu"
- [x] T07 — Create footer partial (contact, quick links, services, enamad) |
  files: `templates/partials/_footer.html` | commit: "feat(base): add v2 footer partial"
- [x] T08 — Create pre-footer CTA partial in new pill style |
  files: `templates/partials/_cta.html`, `apps/home/models.py`,
  `apps/home/migrations/0007_*`, `apps/home/admin.py` |
  commit: "feat(base): add v2 cta partial"
- [x] T09 — Rewrite `base.html` to compose new partials, local deferred
  assets, toast container, scroll progress; keep block names (title,
  description, og_title, og_description, extra_css, extra_head, content,
  afterPrefooter, extra_js) |
  files: `templates/base.html` | commit: "feat(base): rewrite layout with v2 header footer cta"

### Phase 2 — shared JS + static assets

- [x] T10 — Port the `new/` page script into `static/js/pixoria.js` (Lenis,
  reveal, counters, magnetic, tilt, float, scrollspy, menu, FAQ, portfolio
  filter, testimonial slider, toast) |
  files: `static/js/pixoria.js` | commit: "feat(js): add shared pixoria interaction layer"
- [x] T11 — Port hero Three.js scene into a lazy, disposable module |
  files: `static/js/hero-scene.js` | commit: "feat(js): add lazy hero three.js scene"

### Phase 3 — home page models

- [ ] T12 — Extend home models for the new sections (Hero fields, new
  HomeAboutSection, ClientMarqueeItem mark/accent, Service visual + chips,
  WhyFeature/ProcessStep/StatItem/TechSkill icons, ServiceTestimonial
  kind/media, HomeSection keys) + migrations |
  files: `apps/home/models.py`, `apps/home/migrations/`, `apps/services/models.py`,
  `apps/services/migrations/` | commit: "feat(home): add v2 section model fields" — split as T12a/T12b if too big
- [ ] T13 — Register/adjust admin for the new fields (help_text, list_editable) |
  files: `apps/home/admin.py`, `apps/services/admin.py` | commit: "feat(admin): wire v2 home section fields"

### Phase 4 — home page templates

- [ ] T14 — Update `home/index.html` + view context for new section keys |
  files: `templates/home/index.html`, `apps/home/views.py` | commit: "feat(home): render v2 section keys"
- [ ] T15 — Convert `_hero.html` to the v2 hero (3D mount + fallback) |
  files: `templates/home/sections/_hero.html` | commit: "feat(home): convert hero section to v2"
- [ ] T16 — Add `_about.html` (short intro, DB-driven) |
  files: `templates/home/sections/_about.html` | commit: "feat(home): add about section"
- [ ] T17 — Convert `_services.html` (4 bespoke service cards) |
  files: `templates/home/sections/_services.html` | commit: "feat(home): convert services section to v2"
- [ ] T18 — Convert clients → `_trusted.html` (brand plates marquee) |
  files: `templates/home/sections/_trusted.html` | commit: "feat(home): convert clients to trusted marquee"
- [ ] T19 — Convert works → `_portfolio.html` (filterable grid) |
  files: `templates/home/sections/_portfolio.html` | commit: "feat(home): convert works to filterable portfolio grid"
- [ ] T20 — Convert `_why.html`, `_process.html` |
  files: `templates/home/sections/_why.html`, `templates/home/sections/_process.html` | commit: "feat(home): convert why and process sections to v2"
- [ ] T21 — Convert `_testimonials.html` (text/video/audio cards + slider) |
  files: `templates/home/sections/_testimonials.html` | commit: "feat(home): convert testimonials to v2 slider"
- [ ] T22 — Convert `_tech.html`, `_stats.html` |
  files: `templates/home/sections/_tech.html`, `templates/home/sections/_stats.html` | commit: "feat(home): convert tech and stats sections to v2"
- [ ] T23 — Convert `_articles.html` (blog cards), `_faq.html` (accordion) |
  files: `templates/home/sections/_articles.html`, `templates/home/sections/_faq.html` | commit: "feat(home): convert articles and faq sections to v2"
- [ ] T24 — Rework `_contact.html` lead form into v2 style (HTMX kept) |
  files: `templates/home/sections/_contact.html`, `_lead_form.html`, `_lead_success.html` | commit: "feat(home): restyle lead form to v2"
- [ ] T25 — Update `seed_home_content` with the new Persian copy from `new/` |
  files: `apps/home/management/commands/seed_home_content.py` | commit: "feat(home): seed v2 persian content"

### Phase 5 — 404 page

- [ ] T26 — Rebuild `templates/404.html` in v2 style (extends base, gold 404
  watermark, links, optional DB copy) and verify handler404 with a temp route |
  files: `templates/404.html` | commit: "feat(404): redesign not found page in v2 style"

### Phase 6 — About page

- [ ] T27 — Extend about models for the v2 about page (hero, story, journey
  timeline, stats, clients wall, CTA) + migration + admin |
  files: `apps/core/models.py`, `apps/core/migrations/`, `apps/core/admin.py` | commit: "feat(about): add v2 about page models"
- [ ] T28 — Rebuild `templates/core/about.html` from `new/about.html` |
  files: `templates/core/about.html`, `apps/core/views.py` | commit: "feat(about): rebuild about page in v2 style"

### Phase 7 — Contact page

- [ ] T29 — Extend contact models for v2 (info cards, subject choices, FAQ,
  cities block) + migration + admin |
  files: `apps/contact/models.py`, `apps/contact/migrations/`, `apps/contact/admin.py` | commit: "feat(contact): add v2 contact models"
- [ ] T30 — Rebuild `templates/contact/contact.html` from `new/contact.html`
  with a working Django/HTMX form (validation, Persian messages, honeypot,
  submissions in admin) |
  files: `templates/contact/contact.html`, `apps/contact/views.py` | commit: "feat(contact): rebuild contact page with working form"

### Phase 8 — Cleanup

- [ ] T31 — Verify no broken references after base rewrite (grep for removed
  classes/tags), fix `templates/registration/login.html`,
  `templates/admin/login.html`, `templates/blog/*` header/footer assumptions |
  commit: "fix(templates): align remaining pages with v2 base"
- [ ] T32 — Delete old frontend files: unreferenced static CSS/JS
  (`static/css/{styles,site,blog}.css`, `static/js/main.js`, `cursor.js`,
  `header-motion.js`, `home-motion.js`, `footer-stars.js`, `motion.js`,
  `pixoria-bg/`, `engine/`, root-level duplicates) and obsolete templates/
  components after grep verification; one commit per group |
  commit: "chore: remove obsolete v1 frontend assets"
- [ ] T33 — Final checks: `manage.py check`, `makemigrations --check --dry-run`,
  `collectstatic --dry-run`, render home/about/contact/404 with an empty DB;
  then delete `new/` |
  commit: "chore: remove new/ prototype after migration"

## Current status

T01–T11 done — Phases 0–2 complete (foundation, base chrome, interaction +
hero JS). Next: T12 (extend home models for the new sections). hero-scene.js
verified with `node --check` (valid ESM, local three.module.js import).
