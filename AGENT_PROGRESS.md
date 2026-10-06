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
- **D18 — Pricing removed from the home page (user directive).** The
  `packages` section is dropped from the home rendering entirely: removed
  from `HomeSection.KEY_CHOICES`, from the seed command's
  `RENDERED_SECTIONS`/`SECTION_ORDER`/`SECTION_TITLES` and its
  `seed_packages()` method, from the `home` view context (+ its imports), the
  `templates/home/sections/_packages.html` partial deleted, and the existing
  `packages` HomeSection row deleted from the DB. The `PackagesSection`/
  `Package`/`PackageFeature` MODELS stay (data untouched, still in the admin)
  — they are simply no longer reachable from the home page. Mention of
  «پکیج» remaining on the page are FAQ answer prose, not the section.
- **D19 — Home model extensions (T12).** (a) `HeroSection` gains `eyebrow`,
  `cta_primary_*` / `cta_secondary_*` (URL-name, path or `#anchor`, defaults
  `#contact` / `#portfolio`; empty secondary URL hides the button), and a
  new `HeroStat` child (value/label/icon — plain text row like «+۵۰۰
  کسب‌وکار مشاوره‌شده», not a counter). `HeroMarqueeItem` stays (unused in
  v2, model kept per D1). (b) New singletons `HomeAboutSection` (eyebrow,
  title, two paragraphs, csv `chips`, latin `footer_label`) with a
  `HomeAboutStat` child (icon + counter fields, mirrors `StatItem`) — the
  about section's four glass counters are a *separate* stat set from the
  dark `stats` section, so a second model was added rather than overloading
  `StatItem` with two FKs. (c) New singletons `TrustedSection` and
  `TestimonialSection` (the trusted/testimonials headers had no model at
  all). (d) `eyebrow` added to every section-settings model
  (FeaturedWork, Services, Stats, Process, Why, Tech, Faq,
  LatestArticles, Contact); old `subtitle` kept intact for the old
  partials until they are replaced. (e) `ClientMarqueeItem` gains `mark`
  (short plate text) + `accent` (gold/royal). (f) `ProcessStep`,
  `StatItem`, `TechSkill` gain optional Lucide `icon` fields validated by
  `validate_icon_name`. (g) `HomeSection.KEY_CHOICES` now exactly matches
  the v2 order: hero, about, services, trusted, portfolio, why, process,
  testimonials, tech, stats, blog, faq, contact. Data migration `0010`
  renames the existing rows (clients→trusted, works→portfolio,
  articles→blog) and deletes `manifesto`; empty stub partials
  `_about/_trusted/_portfolio/_blog.html` were created so `home/index.html`
  keeps rendering 200 until T14–T25 fill them (the `key` rename would
  otherwise raise TemplateDoesNotExist). The seed command's key maps were
  updated to the same names/orders.
- **D20 — Services model extensions (T12b).** `Service` gains `icon`
  (Lucide), `visual` (none/browser/terminal/palette/diamond — the bespoke
  card artwork in `_services.html`), `card_span` (wide 7 / narrow 5
  columns, independent of `visual` so the admin controls the bento layout),
  `chips` (csv, `get_chips_list()` helper) and `badge` (floating glass
  label like «۹۹/۱۰۰ · Core Web Vitals»). `ServiceTestimonial` gains `kind`
  (text/video/audio), `video_poster`, `video_duration`, `audio_title`,
  `audio_project`, `audio_duration` (all durations in **seconds** as
  integers — templates format them with `fa_digits`; `pixoria.js` still
  hardcodes 48/65 and T21 will wire them through `data-*` attributes) and
  `rating` (1–5, default 5). `text` is now blank because video/audio cards
  carry no quote.
- **D21 — Trusted marquee data (T18).** `seed_home_content.seed_clients()` is
  authoritative for the client table: brands not in the v2 design are deleted
  (`exclude(name__in=…)`), missing ones created, existing ones left alone (the
  file-wide "never overwrite admin edits" rule). This cleaned up 9 stale v1
  rows (آبانسا، دیجی‌کالا، اسنپ، …). The command also reconfigures
  `sys.stdout` to UTF-8 in `handle()` because a Windows cp1252 console raises
  UnicodeEncodeError on the Persian progress messages.
- **D22 — HomeSection order aligned to v2 (T20).** The `HomeSection` rows
  still carried v1 `order` values (process 50 / why 60, about and trusted both
  10, blog last at 130), so the v2 partials rendered in the wrong sequence and
  the section transitions broke — every v2 partial assumes a fixed neighbour
  (trusted's rounded top sits over the dark services section, portfolio's
  cream divider sits on trusted's cream2, why's `clip-path` sits on
  portfolio's ink, process's divider sits on why's cream). The rows were
  renumbered once to the `KEY_CHOICES` order (hero 10 … contact 130) and all
  set active. The `order`/`is_active` fields stay admin-editable; this was a
  one-time alignment like the T17/T19 copy fixes.
- **D23 — Why/process content aligned (T20).** `WhySection`,
  `WhyFeature` (6 rows), `ProcessSection` and `ProcessStep` rows were updated
  in place to the v2 copy (eyebrow «چرا پیکسوریا؟» / «روش کار مأ»، titles with
  `[[ ]]` markers, the design's six reasons and five steps with their Lucide
  icons — badge-check, gem, zap, trending-up, shield-check, heart-handshake /
  message-circle, search, pen-tool, code-xml, party-popper). The 5th process
  step was missing from the v1 data and was created; `WhyFeature.size` is
  unused by v2 and was cleared. The seed still holds the v1 copy — T25
  replaces it.
- **D24 — Media cards are data-driven (T21).** `pixoria.js`
  `initMediaCards` was rewritten to iterate `[data-video-card]` /
  `[data-audio-card]` instead of the hardcoded `#v-*` / `#a-*` IDs, so the
  slider may hold any number of video/audio cards, and each card's duration is
  read from the `data-video-card` / `data-audio-card` attribute itself (the D20
  promise — 48/65 are no longer hardcoded). Inner elements are looked up with
  `card.querySelector("[data-v-play]")` etc. `input.css`'s `#a-play` icon rules
  became `.play-btn` class rules for the same reason. A new `fa_duration`
  filter (`apps/core/templatetags/fa_digits.py`) formats seconds as «۰:۴۸».
- **D25 — T25 seed copy + the one-time alignment that has to run with it.**
  The seed now carries the v2 copy for every section whose prose the design
  rewrites: `HeaderSettings.cta_text` «مشاوره رایگان» (matches the header
  pill), `CTASection` (eyebrow «برند شما، امضای ما»), `LatestArticlesSection`
  (eyebrow «مجلهٔ پیکسوریا»), `ContactSection` (eyebrow «شروع همکاری»), and the
  stats / tech / why / process / FAQ blocks (v2 icons, labels, questions — the
  v1 `subtitle`/`level`/`category`/`description` values v2 never renders are
  seeded empty). Two collection cleanups follow the D21 pattern: `TechSkill`
  and `FaqItem` rows whose name/question is not in the v2 list are deleted, so
  re-seeding an old v1 DB converges instead of accumulating duplicates
  (verified: 5 v1 FAQ rows → 6 v2 rows; a second run adds and deletes
  nothing). But `first_or_create` cannot update singletons that already
  exist, so the four section singletons + the header CTA + the empty
  `SiteSettings` chrome fields (`tagline`, `mega_*`, `trust_*`, `website`)
  were nudged in place once with a throwaway script, exactly like the D22/D23
  one-shots. **GOTCHA from this task:** `SiteSettings` held the user's *real*
  content (footer description, street address, established year, socials
  pointing at their own project), not seed placeholders, so a blanket
  alignment clobbered three fields and created four duplicate `SocialLink`
  rows; they were restored and the duplicates deleted. Rule going forward:
  dump `SiteSettings` first and only write fields that are empty or match a
  known seed value — never overwrite a field that already holds data. Also
  `ALLOWED_HOSTS` excludes `testserver`, so `Client().get("/")` returns 400
  inside `manage.py shell`; use `Client(HTTP_HOST="localhost")`.
- **D26 — Reusable components.** Two layers: (1) CARD partials
  (`templates/components/_project_card.html`, `_article_card.html`,
  `_testimonial_card.html`) used everywhere a card renders; (2) SECTION
  components as inclusion tags with parameters (`service`, `category`,
  `exclude`, `limit`) that run their own query, so views/pages do not need to
  pass data in context. Every component: optimized query
  (`select_related`/`prefetch_related` + `limit`), renders NOTHING when there
  is no data, no hard-coded Persian content except tiny UI labels, no
  hard-coded element IDs (use `data-*` hooks + per-instance JS init so the
  same component works more than once per page), and `highlight` for headings.
  Component JS lives in `static/js/pixoria.js` (or one small separate deferred
  module), initialized per `[data-*]` instance — no CDN, no new libraries.
- **D27 — Design language for pages without a `new/` design (portfolio,
  blog).** Before designing, study `static/src/input.css` (tokens
  ink/cream/gold/royal, `glass`, `tile`, `btn`, `eyebrow`, `divider`,
  `blog-card`, `type-chip`, …), the converted home partials in
  `templates/home/sections/`, the header/footer/CTA partials and the existing
  3D/visual elements. New pages reuse the SAME classes, spacing, radius
  variants, section rhythm (dark ↔ cream transitions), animations
  (`data-reveal`, `data-delay`, magnetic/tilt where already used) and
  typography (Vazirmatn + Space Grotesk latin). Do not invent a new visual
  style. Add new CSS classes to `static/src/input.css` only when truly needed,
  then run `npm run build`. Hero areas of inner pages need their own top
  padding — the header is fixed and overlays (see the `pt-[clamp(...)]`
  precedent in `components/page_hero.html`).
- **D28 — 404 page (T26).** `templates/404.html` extends `base.html` and
  renders a pure-CSS "lost solar system" scene (`.nf-*` classes in
  `input.css`) that echoes the hero's crystal-planet idea without any
  WebGL/JS: gold planet with Saturn rings, two orbiting moons, twinkling
  stars, a shooting meteor, floating shards/orbs, and a giant stroked `۴۰۴`
  watermark. No 3D was added on purpose — a 404 must never block on asset
  loading, and CSS-only keeps it instant on low-end devices; reduced-motion
  kills every `.nf-*` animation and pins the stars at a static opacity. The
  copy is Persian with a `highlight`-marked h1 and links to home/contact plus
  an `s-chip` row to the main pages; `noindex` meta via `extra_head`.
  Verified through `handler404` with `override_settings(DEBUG=False)` and a
  non-existent URL (status 404, all content present) — no temporary route was
  needed, so nothing had to be removed afterwards.
- **D29 — Portfolio grid trim (T27).** The home portfolio grid is
  `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`; the view caps featured items at
  9 (ordered by `order`, `id`) and, when there are more than 3, trims the list
  to the largest multiple of 3 so the last `lg` row is never one orphan tile.
  Counts ≤ 3 are shown as-is on purpose — hiding real content to satisfy the
  grid math is worse than a short row (the DB currently has only one featured
  project, which would have been trimmed to zero by a naive `% 3` slice).
- **D30 — Card partials + the `{% cycle %}` include gotcha (T28).**
  `templates/components/_project_card.html` (props `project`, `filter_key`,
  `radius`, `class`, `style`), `_article_card.html` (`article`, `delay`,
  `class`, `style`) and `_testimonial_card.html` (`t`, `class` — the
  text/video/audio branches in one file) replace the markup that was inline in
  the home sections. `_portfolio.html`, `_blog.html` and `_testimonials.html`
  now `{% include %}` them, and the render output is byte-identical apart from
  attribute order (verified by diffing the rendered page before/after — the
  class and style *multisets* are equal). Section-specific hooks stay with the
  caller: the filter hook (`pf-item` + `data-cat`) only prints when
  `filter_key` is passed, and the slider's sizing (`w-[min(88vw,400px)]
  shrink-0 snap-center`) comes from the section's `class` prop; `t-card` is
  baked into the testimonial card because it is the slider's card hook (it
  carries no styling). **GOTCHA:** `{% cycle %}` inside an `{% include %}`d
  template resets on every inclusion (the included template gets a fresh
  `render_context`), so the per-card stagger values (the project card's
  rotating border-radius, the article card's reveal delay) are generated with
  `{% cycle ... as x silent %}` in the *caller's* loop and passed as props —
  and the `silent` keyword is mandatory in Django 5.2, otherwise the value is
  printed into the page as stray text. The v1 `components/cards/*.html` cards
  stay until the still-unconverted pages (`blog/partials/article_cards.html`,
  `services/detail.html`) are rebuilt (T39/T42); new pages must use the new
  partials.

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

- [x] T12 — Extend home models for the new sections (Hero fields, new
  HomeAboutSection, ClientMarqueeItem mark/accent, Service visual + chips,
  WhyFeature/ProcessStep/StatItem/TechSkill icons, ServiceTestimonial
  kind/media, HomeSection keys) + migrations |
  files: `apps/home/models.py`, `apps/home/migrations/0009_*`, `0010_*`,
  `apps/services/models.py`, `apps/services/migrations/0006_*`,
  `apps/home/management/commands/seed_home_content.py`,
  `templates/home/sections/_{about,trusted,portfolio,blog}.html` (stubs) |
  commit: "feat(home): add v2 section model fields" — done as T12a (home) +
  T12b (services) in one commit
- [x] T13 — Register/adjust admin for the new fields (help_text, list_editable) |
  files: `apps/home/admin.py`, `apps/services/admin.py`,
  `apps/core/icon_utils.py` (shared `IconPreviewMixin` + `icon_preview_html`) |
  commit: "feat(admin): wire v2 home section fields"

### Phase 4 — home page templates

- [x] T14 — Update `home/index.html` + view context for new section keys |
  files: `templates/home/index.html`, `apps/home/views.py`,
  `templates/home/sections/_faq.html` (duplicate FAQ JSON-LD removed) |
  commit: "feat(home): render v2 section keys"
- [x] T15 — Convert `_hero.html` to the v2 hero (3D mount + fallback) |
  files: `templates/home/sections/_hero.html`,
  `apps/home/management/commands/seed_home_content.py` (v2 hero copy +
  HeroStat seed, imports) | commit: "feat(home): convert hero section to v2"
- [x] T16 — Add `_about.html` (short intro, DB-driven) |
  files: `templates/home/sections/_about.html`,
  `apps/home/management/commands/seed_home_content.py` (HomeAboutSection +
  HomeAboutStat copy, TrustedSection/TestimonialSection/FeaturedWork/
  Services eyebrows, v2 client marquee marks) |
  commit: "feat(home): add about section"
- [x] T17 — Convert `_services.html` (4 bespoke service cards) |
  files: `templates/home/sections/_services.html`,
  `apps/home/management/commands/seed_home_content.py` (`seed_services`
  applies v2 visual/card_span/chips/badge per service) |
  commit: "feat(home): convert services section to v2"
- [x] T18 — Convert clients → `_trusted.html` (brand plates marquee) |
  files: `templates/home/sections/_trusted.html` |
  commit: "feat(home): convert clients to trusted marquee"
- [x] T19 — Convert works → `_portfolio.html` (filterable grid) |
  files: `templates/home/sections/_portfolio.html`, `apps/home/views.py` |
  commit: "feat(home): convert works to filterable portfolio grid"
- [x] T20 — Convert `_why.html`, `_process.html` |
  files: `templates/home/sections/_why.html`, `templates/home/sections/_process.html` |
  commit: "feat(home): convert why and process sections to v2"
- [x] T21 — Convert `_testimonials.html` (text/video/audio cards + slider) |
  files: `templates/home/sections/_testimonials.html`, `static/js/pixoria.js`,
  `static/src/input.css`, `apps/core/templatetags/fa_digits.py` |
  commit: "feat(home): convert testimonials to v2 slider"
- [x] T22 — Convert `_tech.html`, `_stats.html` |
  files: `templates/home/sections/_tech.html`, `templates/home/sections/_stats.html`,
  `apps/home/views.py`, `static/js/pixoria.js` |
  commit: "feat(home): convert tech and stats sections to v2"
- [x] T23 — Convert `_articles.html` (blog cards), `_faq.html` (accordion) |
  files: `templates/home/sections/_blog.html` (replaces the v1 `_articles.html`
  carousel partial, deleted), `templates/home/sections/_faq.html` |
  commit: "feat(home): convert articles and faq sections to v2"
- [x] T24 — Rework `_contact.html` lead form into v2 style (HTMX kept) |
  files: `templates/home/sections/_contact.html`, `_lead_form.html`,
  `_lead_success.html`, `static/src/input.css` (`.field` + `.field-err`) |
  commit: "feat(home): restyle lead form to v2"
- [x] T25 — Update `seed_home_content` with the new Persian copy from `new/` |
  files: `apps/home/management/commands/seed_home_content.py` | commit: "feat(home): seed v2 persian content"

### Phase 5 — 404 page

- [x] T26 — Rebuild `templates/404.html` in v2 style: beautiful, attractive
  Persian 404 matching the site's design language and its 3D/visual style (gold
  404 watermark, lightweight reuse of the hero crystal/visual idea, lazy +
  paused + disposable if WebGL is used, CSS/poster fallback, reduced-motion
  respected). Persian copy, home button, links to main pages. Verify handler404
  / DEBUG=False with a temporary route that is removed afterwards |
  files: `templates/404.html`, `static/src/input.css` |
  commit: "feat(404): redesign not found page in v2 style"

### Phase 5b — Home tweak + shared components

- [x] T27 — Home portfolio grid becomes 3 columns (`grid-cols-1
  md:grid-cols-2 lg:grid-cols-3`), keep the filter, radius variants, empty
  state. Limit rendered items to a multiple of 3 (e.g. 6 or 9) from the view.
  Verify no orphan/ugly tile layout at all breakpoints |
  files: `templates/home/sections/_portfolio.html`, `apps/home/views.py` |
  commit: "feat(home): make portfolio grid three columns"
- [x] T28 — Extract CARD partials (no visual change):
  `templates/components/_project_card.html`, `_article_card.html`,
  `_testimonial_card.html` (text/video/audio kinds). Home sections must use
  them | files: `templates/components/*`, `templates/home/sections/*` |
  commit: "feat(components): extract reusable card partials"
- [ ] T29 — Testimonials SECTION component: inclusion tag
  `{% testimonials_slider service=None limit=9 title=... %}` (templatetag in
  `apps/core/templatetags/` or the app that owns the model). With `service`
  given → only that service's testimonials; without → featured/global ones (as
  the home page does now). Section renders nothing if there is no data.
  Refactor the slider JS in `static/js/pixoria.js` from fixed `#t-*` IDs to
  per-instance `[data-slider]` initialization (multiple sliders per page must
  work, no duplicate IDs). Home must use the component |
  files: `apps/core/templatetags/*`, `static/js/pixoria.js`,
  `templates/home/sections/_testimonials.html` |
  commit: "feat(components): testimonials slider inclusion tag"
- [ ] T30 — Generic carousel component + CAROUSEL SECTIONS:
  `{% projects_carousel exclude=None category=None service=None limit=8 %}` and
  `{% articles_carousel exclude=None category=None limit=8 %}` built on the
  card partials. Lightweight dependency-free carousel (CSS scroll-snap + small
  per-instance JS in pixoria.js: prev/next buttons, RTL-aware direction,
  keyboard accessible, drag/touch friendly, `aria-label`s). No new library.
  Section hides itself if empty. Home blog section should use the articles
  component | files: `apps/core/templatetags/*`, `static/js/pixoria.js`,
  `templates/components/*`, `templates/home/sections/_blog.html` |
  commit: "feat(components): add projects and articles carousels"

### Phase 6 — About page (from `new/about.html`)

- [ ] T31 — Extend about models for the v2 about page (hero, story,
  journey/timeline, stats, values, team, clients wall, CTA — whatever exists
  in `new/about.html`), reuse existing `core.About*` models and `TeamMember`;
  add only what is missing; migration + admin (Persian
  help_text/verbose_name, inlines, `order`, `is_active`); optional-content
  rules; seed command with the original Persian copy from `new/about.html`
  (idempotent, no overwriting) |
  files: `apps/core/models.py`, `apps/core/migrations/`, `apps/core/admin.py`,
  `apps/core/management/commands/*` | commit: "feat(about): add v2 about page models"
- [ ] T32 — Rebuild `templates/core/about.html` from `new/about.html`: extend
  `base.html`, REMOVE the duplicated hard-coded header/footer/CTA from the new
  file (base ones are the reference), bind everything to the models, use
  `highlight` for colored words, `{% icon %}` for icons, `fa_digits`/counters
  where needed, local JS only, skip empty sections. Update `apps/core/views.py`
  | files: `templates/core/about.html`, `apps/core/views.py` |
  commit: "feat(about): rebuild about page in v2 style"

### Phase 7 — Contact page (from `new/contact.html`)

- [ ] T33 — Extend contact models for v2 (info cards, subject/project-type/
  budget/start-time choices, FAQ, cities/map block, working hours, socials)
  reusing existing `contact.*` models; migration + admin + seed (same rules) |
  files: `apps/contact/models.py`, `apps/contact/migrations/`,
  `apps/contact/admin.py`, `apps/contact/management/commands/*` |
  commit: "feat(contact): add v2 contact models"
- [ ] T34 — Rebuild `templates/contact/contact.html` from `new/contact.html`:
  extends `base.html`, no duplicated header/footer/CTA, working form (Django
  form/model, saved `ContactSubmission` visible in admin, CSRF, validation
  with Persian error/success messages, honeypot + simple rate limit like the
  home lead form, HTMX with `data-toast` success announcement per D16,
  optional email notification only if email settings already exist). Reuse the
  `.field` styles from `static/src/input.css` |
  files: `templates/contact/contact.html`, `apps/contact/views.py` |
  commit: "feat(contact): rebuild contact page with working form"

### Phase 8 — Portfolio pages (no design in `new/`: design them)

- [ ] T35 — Review `portfolio` models vs the planned pages; add only what is
  missing (e.g. optional gallery images inline, results/metrics via existing
  `ProjectStat`, technologies/tags, optional related testimonial link, SEO
  fields), all optional; migration + admin + seed if needed |
  files: `apps/portfolio/models.py`, `apps/portfolio/migrations/`,
  `apps/portfolio/admin.py` | commit: "feat(portfolio): extend models for v2 pages"
- [ ] T36 — Portfolio LIST page `templates/portfolio/list.html`: v2 hero
  (eyebrow + `highlight` title from admin-editable settings if reasonable),
  category filter (server-side by existing URL/query if the view supports it,
  else JS filter), 3-column grid using `_project_card.html`, pagination or
  HTMX load-more, empty state, CTA from base |
  files: `templates/portfolio/list.html`, `apps/portfolio/views.py` |
  commit: "feat(portfolio): rebuild list page in v2 style"
- [ ] T37 — Portfolio DETAIL page `templates/portfolio/detail.html`: hero with
  cover image, meta (client, year, service type, categories, external link),
  challenge/solution sections, stats counters (`ProjectStat`), gallery if
  present, description (rich text styled), next/previous project,
  `{% projects_carousel exclude=object %}` as related projects, optional
  `{% testimonials_slider service=... %}` only if it makes sense. JSON-LD +
  meta blocks | files: `templates/portfolio/detail.html`,
  `apps/portfolio/views.py` | commit: "feat(portfolio): rebuild detail page in v2 style"

### Phase 9 — Blog pages (no design in `new/`: design them)

- [ ] T38 — Review `blog` models; add only what is missing (e.g. featured
  flag, optional cover alt text, SEO fields exist already); migration + admin
  if needed. Add a reusable rich-text typography style for TinyMCE `HTMLField`
  content in `static/src/input.css` (headings, lists, quotes, images, tables,
  code, links) in the gold/cream/ink language, RTL-correct |
  files: `apps/blog/models.py`, `apps/blog/migrations/`, `apps/blog/admin.py`,
  `static/src/input.css` | commit: "feat(blog): extend models and add prose styles"
- [ ] T39 — Blog LIST page `templates/blog/list.html`: v2 hero, featured
  article, category filter, search only if already supported by the view, grid
  using `_article_card.html`, keep the existing `blog:load` HTMX load-more
  behavior working with the new cards (update the `blog` partial used by
  `blog:load`), empty state | files: `templates/blog/list.html`,
  `apps/blog/views.py`, `templates/blog/*` |
  commit: "feat(blog): rebuild list page in v2 style"
- [ ] T40 — Blog DETAIL page `templates/blog/detail.html`: hero with cover,
  category, Jalali date (`fa_jdate`), reading time (`fa_digits`), author,
  reading-progress bar, article body with the typography style, auto table of
  contents from headings only if it can be done cheaply (small local JS, no
  library), tags, share buttons (plain links, no third-party scripts),
  `{% articles_carousel exclude=article category=article.category %}` as
  related posts, Article JSON-LD, meta blocks. Keep
  `blog:tinymce-image-upload` untouched | files: `templates/blog/detail.html`,
  `apps/blog/views.py`, `static/js/pixoria.js` |
  commit: "feat(blog): rebuild detail page in v2 style"

### Phase 10 — Cleanup

- [ ] T41 — Verify no broken references (grep for removed
  classes/tags/includes), fix `templates/registration/login.html`,
  `templates/admin/login.html`, proposal page and any remaining page that
  still assumes the old base | commit: "fix(templates): align remaining pages with v2 base"
- [ ] T42 — Services list/detail: no converted design in this migration. Give
  them minimal placeholders that extend the new `base.html` ONLY IF they are
  currently broken/unstyled; list them under `## Pending pages` in this file.
  Do NOT redesign them now (the testimonials/projects/articles components must
  already accept a `service` parameter so these pages can use them later) |
  commit: "fix(services): placeholder pages for v2 base"
- [ ] T43 — Delete ALL old frontend files (unreferenced static CSS/JS, old
  templates/partials/components, unused template tags/context
  processors/views/URLs created only for old templates). Before deleting, list
  candidates in this file and verify with a project-wide grep. One small commit
  per group | commit: "chore: remove obsolete v1 frontend assets"
- [ ] T44 — Final checks: `python manage.py check`,
  `makemigrations --check --dry-run`, `collectstatic --dry-run`, render
  home/about/contact/404/portfolio/blog (list + detail) with an EMPTY database
  and with seeded data, Lighthouse-minded review; then delete `new/` as a
  separate final commit | commit: "chore: remove new/ prototype after migration"

## Current status

T01–T28 done. Next: T29 — testimonials SECTION component: an inclusion tag
`{% testimonials_slider service=None limit=9 title=... %}` (filters by service
when one is given, featured/global otherwise, renders nothing without data),
and the slider JS in `static/js/pixoria.js` refactored from the fixed `#t-*`
IDs to per-instance `[data-slider]` initialization so several sliders can live
on one page.

