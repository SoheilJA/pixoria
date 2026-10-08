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

- `apps.home`: `home:home` (`/`).
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

Pending pages (no new design in `new/`): services list/detail (see
`## Pending pages` at the end — they are the last unstyled pages and T42's
only scope). The portfolio and blog pages had no `new/` design either but were
designed in the v2 language directly (T35–T40, see D27) and are done. The
remaining ones still use v1 templates; they extend `base.html`, so the new
base restyles their chrome, but their own markup still assumes old tokens and
needs the T41/T42 pass. Service detail pages exist in `new/services/` but are
out of scope for this migration order (home/about/contact/404 only).

### Pending pages

_(none left — every URL renders in the v2 design now. T42 gave the services
pages minimal placeholders; a full services redesign is deliberately out of
scope for this migration and can pick these templates up later.)_

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
- **D31 — Testimonials slider component (T29).** The whole section (divider,
  stroke-quote watermark, header, controls, scroll-snap track, hint line) moved
  into `templates/components/testimonials_slider.html`, driven by the inclusion
  tag `testimonials_slider(service=None, limit=9, title="", eyebrow="",
  id="testimonials")` in `apps/services/templatetags/testimonial_tags.py` (the
  tag lives with the model owner, `apps.services`). With no `service` it queries
  `show_on_home=True` (exactly what the home view did), with one it queries that
  service's testimonials (unrestricted by `show_on_home` — a service page shows
  its own evidence); ordered by `order`, `id`, capped by `limit` (`int()`-
  coerced so a string variable cannot 500 the page). It renders nothing on an
  empty query, so `templates/home/sections/_testimonials.html` shrank to a
  single tag call passing the `TestimonialSection` singleton's title/eyebrow,
  and the home view dropped its now-unused `testimonials` context entry (and
  the `ServiceTestimonial` import) — `services/detail.html` keeps its own
  separate `testimonials` context and is untouched. The element ids are gone:
  `#t-slider` → `data-slider`, `#t-prev/next/dots` → `data-slider-prev/next/
  dots`, all looked up inside a `data-slider-root` wrapper, and
  `static/src/input.css`'s `#t-slider{.dragging}` rules became `[data-slider]`
  attribute selectors (Tailwind rebuilt). `pixoria.js`'s `initSliders` now loops
  `document.querySelectorAll("[data-slider]")` and initialises each instance
  independently (dots, scroll progress, autoplay, drag all close over that
  instance's `slider`), so several sliders can share a page; the default section
  `id` stays `testimonials` for anchors and is overridable. Verified in a
  rolled-back transaction: empty service renders zero characters, a service with
  text/video/audio testimonials renders one card per kind, `limit` truncates,
  and two tag calls on one page yield two `data-slider-root`s with no duplicate
  ids. Node `--check` passes on the module.
- **D32 — Carousels (T30).** The v1 carousel (the `.carousel*` classes, the
  `per_view`/`gap`/`autoplay` config data attributes and
  `static/js/core/carousel.js`, which v2's `base.html` never loaded anyway) is
  gone: `components/carousel.html` is rewritten as a scroll-snap shell with
  `data-carousel` / `data-carousel-track` / `-prev` / `-next` / `-dots` hooks,
  reusing the testimonials' `.ctrl-btn` buttons and the renamed `.slider-dot`
  dot style (was `.t-dot`, renamed now that two components share it). The
  `{% carousel %}…{% endcarousel %}` block tag in `component_tags.py` stays —
  it only forwards `class`/`id` now that the config props are dead — and its
  `content` slot is a `SafeString`, so no double escaping. Two new inclusion
  tags next to their models: `apps/portfolio/templatetags/projects_tags.py`
  (`projects_carousel(exclude, category, service, limit=8)`) and
  `apps/blog/templatetags/articles_tags.py`
  (`articles_carousel(exclude, category, limit=8)`). Both query themselves
  (`Portfolio` ordered by `order`; `Article` filtered to `published` and
  non-future, ordered by `-published_at`), accept `exclude` as a model
  instance and `category` as either an instance or a slug, coerce `limit` with
  `int()`, and render nothing on an empty query. `service` filters the free-text
  `service_type` field (a `Service` instance resolves to its `title`) because
  `Portfolio` has no FK to `Service` — see T35 if a real relation is wanted.
  `pixoria.js` gained `initCarousels` (dots per slide, scroll-progress active
  dot, prev/next with wrap-around, keyboard on the focusable track —
  `ArrowLeft` advances in RTL — and mouse drag) and the shared
  `enableTrackDrag(track)` helper that the testimonial slider now also uses.
  The home blog section is now `blog_section` (header + link) + one
  `{% articles_carousel %}` call, so the view's `latest_articles` entry and
  the `Article`/`timezone` imports were dropped. Card widths inside a carousel
  are the caller's job (`w-[min(86vw,360px)] … lg:w-[min(30vw,400px)] shrink-0
  snap-start`). Verified in a rolled-back transaction: empty queries render
  only whitespace, `exclude`/`category`(instance and slug)/`limit` behave, and
  two carousels on one page produce two independent tracks with no element ids.

- **D33 — About model extensions (T31).** `new/about.html` has five sections
  (hero → story → journey → stats → clients; the final cream CTA is the shared
  `_cta.html` from base, and the header/footer come from base too). Extended the
  existing models instead of adding parallel ones: `AboutPageHero` gains
  `eyebrow` and the same CTA pair as `HeroSection` (`cta_primary_*` /
  `cta_secondary_*`, `nav_url`-resolvable, empty secondary URL hides the
  button); `AboutStory` gains `eyebrow`, `title` (with `[[ ]]`), `body` (extra
  paragraphs, newline-separated), `chips` (csv), `quote`, `image` /
  `image_alt` / `image_caption`; `AboutStat` gains the `StatItem` counter trio
  (`value` int + `prefix` / `suffix`) plus a Lucide `icon` — the old `number`
  CharField stays in the DB (untouched) for the v1 template and is unused by v2.
  Three new singletons: `AboutJourneySection` (eyebrow/title/subtitle +
  `badge_icon`/`badge_text` for the floating "+۱۵ سال تجربه" capsule) with an
  `AboutJourneyStep` child (`year` free text — «۱۳۸۹» first / «امروز» last —
  title, subtitle, order), and `AboutClientsSection` (eyebrow/title/subtitle).
  **The clients wall reuses `home.ClientMarqueeItem`** — the DB already holds
  exactly the seven brands the design names, and sharing the table keeps one
  edit point; the about view queries it directly (no new FK, no new client
  model). The hero's orbit pills (طراحی سایت / برنامه‌نویسی / …) come from the
  `Service` table (`Service.objects.all()[:4]`, icon + title), same as the
  mega-menu. There is NO section-registry model for the about page — the v2
  order is fixed in the template with per-section `{% if %}` guards, since
  unlike the home page nothing here needs admin-reorderable sections. The
  `AboutMission` / `AboutValue` / `AboutPre` / `TeamMember` /
  `AboutProcessStep` / `AboutFaq` models and their data stay untouched — they
  simply are not part of the v2 about design (D18 precedent); T43 decides
  their fate. Migration `core.0009`, admin fieldsets + `IconPreviewMixin` on
  `AboutStatAdmin`, new singletons get the usual `has_add_permission` guard.
  Seed: new `apps/core/management/commands/seed_about_content.py` (the core
  app had no management package before — it was created for this command),
  carrying the verbatim Persian copy from `new/about.html`, `first_or_create`
  for singletons, and the D21/D25 collection cleanup for the two collections
  (`AboutJourneyStep` / `AboutStat` delete rows not in the v2 list, then
  `get_or_create` the rest) — this removed the 3 stale v1 stat rows
  («+۵۰ پروژه تحویل شده» …) and seeded the 4 v2 counters. Re-running is a
  clean no-op (verified). The two v1 singletons held old-design prototype copy
  with raw markup («یک استودیو خلاق <br> در مشهد.» / story description with
  `<p><strong>`), which would render as escaped noise through the `highlight`
  filter; per D22/D23/D25 they were nudged in place once with a throwaway
  script after dumping the prior values. **Journey SVG gotcha for T32:** the
  desktop map hardcodes 5 node positions along a fixed path; with DB-driven
  steps the template must distribute nodes itself (position list keyed by
  index, or evenly along the path) and the mobile `<ol>` renders all steps.
- **D34 — About page template (T32).** `templates/core/about.html` fully replaced
  (v1 mission/story/process/team/values/stats/FAQ/pre partials out) with the
  five `new/about.html` sections on top of `base.html`: hero → story → journey
  → stats → clients, then the shared `_cta.html`/`_footer.html` from base —
  every hard-coded duplicate of the header, mega-menu, mobile menu, CTA and
  footer from the prototype was dropped (~1100 lines of chrome). Conversions:
  `[[ ]]` titles via `highlight` (dark variant on the cream sections), all
  `data-lucide` → the local `{% icon %}` sprite, hero CTAs via `{% nav_url %}`,
  digits via `fa_digits`, stats via `data-counter` + `data-prefix`/`-suffix`
  (15+/500+/135+/350+). The hero's orbit pills are built from the `Service`
  table with two independent `{% cycle %}`s per loop iteration (float duration +
  top/right/bottom/left position), so the orbit degrades gracefully to fewer
  pills. **Zero new CSS**: the design's `.ghost-stroke`/`.ghost-stroke-light`
  are the existing `.stroke-title`/`.stroke-title-light`, and `.client-wall`'s
  hover became inline `hover:text-gold-light`. The journey map is computed
  server-side (`journey_points`/`journey_path` in `apps/core/views.py`): the
  design's exact five node positions when there are five steps, otherwise an
  even sinusoidal spread, with a quadratic path drawn *through* the computed
  points so the path and nodes can never disagree; each step is annotated with
  `point_x`/`point_y`/`label_below`/`label_bold`/`label_small` (bold = year for
  the first/last station, title otherwise — mirroring the design's labels).
  The mobile timeline's decorative line moved out of the `<ol>` into a wrapper
  div (the prototype had an invalid `<span>` child of `<ol>`). The story image
  is optional — without it a decorative «پ» tile renders instead of a hole
  (the seed cannot create image files). `story.body` uses `|linebreaks` inside
  a `space-y-4` wrapper, and `AboutStory.get_chips_list()` mirrors
  `HomeAboutSection`. JSON-LD (Organization + AboutPage + BreadcrumbList) moved
  into `extra_head`, built from `SiteSettings` — only required fields are used
  so conditional commas can never break the JSON. `pixoria.js`'s mouse-parallax
  was generalized from `document.getElementById("home")` to
  `document.querySelectorAll("[data-mouse-parallax]")` and the home hero got
  the attribute (behavior unchanged) so both pages share one init path.
  Verified: `/about/` renders 200 (65 KB) with all five sections, no leaked
  `[[ ]]` markers, zero CDN/lucide references, journey nodes/labels/counters
  correct; with an EMPTY database (rolled-back transaction) every section skips
  and the page still returns 200; home page unaffected (146 KB, 200); node
  module syntax check passes; Tailwind rebuilt (no token changes — just the
  new arbitrary classes).
- **D35 — Contact model extensions (T33).** `new/contact.html` has four
  sections (hero → form → cities/map → FAQ; the CTA and footer come from base).
  Reused what existed and added only the missing pieces. `ContactPageSection`
  gained `eyebrow` + `response_note` (the small "پاسخ‌گویی در روزهای کاری…"
  line under the hero description). The hero's four contact cards render from
  `SiteSettings` (phone / phone_secondary / email / website) — the same single
  source the header/footer already use, so the pre-existing `ContactInfo`
  model (office_title/working_hours/…) is now vestigial for v2 and left
  untouched for T43. New singletons mirroring the home/about pattern:
  `ContactFormSection` (eyebrow/title/description + `button_text` + `note`,
  with a `ContactFormPoint` child — icon + text, order, is_active — for the
  three-point checklist), `ContactMapSection` (eyebrow/title/subtitle +
  `office_name` / `office_note` / `coverage_note` for the radial map's
  labels) and `ContactFaqSection` (eyebrow/title + `footer_question` /
  `footer_cta_text` for the "پاسخ‌تان را پیدا نکردید؟" closing block) with a
  `ContactFaq` child (question/answer/order) — there was NO contact FAQ model
  before (home's `FaqItem` holds different questions). `SubjectChoice`
  (label/order) joins the existing choice models for the form's subject
  select, and `ContactSubmission` gained `email` + `subject`; the v1 fields
  (company/project_type/budget/start_time) stay untouched — the v2 form
  renders name/email/phone/subject/message, and whether the old fields are
  re-introduced later is a T34 decision. Migration `contact.0003`; admin got
  fieldsets for the singletons, a `ContactFormPointInline`, `list_editable`
  orders and the new submissions columns. Seed:
  `apps/contact/management/commands/seed_contact_content.py` (new management
  package in the contact app) with the verbatim Persian copy, the D21-style
  collection cleanup for `ContactFormPoint`/`ContactFaq`, and
  `first_or_create` singletons — the one existing v1 `ContactPageSection` row
  was nudged in place once after dumping its values (D25 pattern). Two seed
  runs are clean no-ops. `/contact/` still renders 200 on the old template
  (T34 replaces it).

- **D39 — Portfolio detail page (T37).** `templates/portfolio/detail.html`
  rebuilt on `base.html` in the D27 design language, replacing the v1 template
  (which still used the deleted `text-ink`/`bg-night`/`px-page` tokens and
  therefore rendered unstyled). Eight sections, alternating dark/cream in the
  v2 rhythm: hero (`bg-ink`, mouse-parallax, `project` stroke watermark,
  breadcrumb trail, category chips linking to `category.filter_url`, highlight
  h1, four glass meta tiles for client/year/service/site) → cover image
  (`bg-ink2`, `divider-flip`, `fetchpriority="high"`) → description (`bg-cream`,
  rounded top corners, sticky sidebar with `get_technologies_list()` as
  `s-chip-light`s) → challenge/solution (`bg-cream2`, two `glass-light` cards,
  only when either field is set) → results (`bg-ink2`, `ProjectStat` cards reusing
  the home `stat-card`/`stat-num`/`stat-icon` classes — `stat.number` is free
  text like «+۳۵٪» so it renders through `fa_digits`, not `data-counter`, since
  it is not a pure number) + the optional `testimonial` FK rendered as one
  `_testimonial_card.html` (a single card, not the slider — the slider tag needs
  a `service` and `Portfolio` has no FK to one; D37) → gallery (`bg-ink`, only
  when `gallery` is non-empty, `cycle` radius + caption slide-in) → other work
  (`bg-ink2`, `{% projects_carousel exclude=portfolio limit=6 %}` + prev/next
  glass tiles). **The prev/next queries were fixed**: the v1 versions compared
  `order` alone, so projects sharing one `order` value were invisible to each
  other; they now mirror the list ordering (`order`, `id`) with a `Q(order__lt) |
  Q(order=..., id__lt)` pair. The whole "other work" section is guarded by
  `{% if prev_portfolio or next_portfolio %}` — that flag is exactly "another
  project exists", which is also the carousel's non-empty condition, so a
  single-project DB renders neither the header nor an empty track. **The view's
  `stats` NameError was fixed**: the T36 prefetch edit dropped
  `stats = portfolio.stats.all()` but left `"stats": stats` in the context, so
  every detail page raised 500; the template now reads the prefetched
  `portfolio.stats.all` directly and the context entry is gone.
  JSON-LD (`CreativeWork` + `BreadcrumbList`) in `extra_head` uses a NEW
  `json` filter (`apps/core/templatetags/json_tags.py`, `ensure_ascii=False` so
  Persian stays readable) instead of raw interpolation, so a quote in a title
  can never break the script block. `meta` description comes from
  `get_meta_description()`. Verified: detail 200 (49 KB bare, 55 KB with
  stats/testimonial/challenge/solution/technologies), 404 on a missing slug,
  200 with a minimal project (no image/categories/stats/gallery — optional
  sections skip), 200 with a single-project DB (related section fully hidden,
  no empty carousel controls), prev/next correct on both neighbours, no leaked
  `[[ ]]`, no CDN references, `manage.py check` + `makemigrations --check`
  clean, home/about/contact/blog/list unaffected, Tailwind rebuilt (no token
  changes — only new arbitrary utilities).

- **D45 — T41 verification + the last three v1 pages (T41).** The three pages
  that still assumed the old chrome — `templates/registration/login.html`,
  `templates/admin/login.html`, `templates/core/proposal.html` — were rebuilt
  in the v2 language: the proposal page now `extends 'base.html'` and both
  logins stay standalone full HTML documents (a login page wants no site
  header/footer/CTA, and the admin login view renders outside the site chrome
  anyway). All three use only local assets (`js/vendor/gsap` +
  `ScrollTrigger` defer, `js/pixoria.js` module), the `{% icon %}` sprite,
  `pixel_wordmark`, the shared `.field`/`.field-err`/`.btn-gold` components and
  the same orb/shard/stroke-title hero vocabulary as the other pages; the
  logins read their brand column and stats from the `site_context` processor
  (`settings`, `stats` = `AboutStat`, so `stat.prefix`/`value`/`suffix` from
  D33 work unchanged). Proposal page: v2 sections (hero with `proposal` stroke
  watermark → screenshots → current-vs-target stats → problems/solutions →
  essential/optional services → price card), each `{% if %}`-guarded, every
  heading through `highlight`, `divider-flip` waves on the dark/cream
  transitions, `noindex` via `extra_head`. One bug was caught in review:
  `prose-ink` sat on the hero's dark `bg-ink` — `.prose-ink` is the LIGHT
  variant per D40, so it became `.prose-cream`.
  **Verification (new `scripts/render_check.py`, kept for T44):** every live
  URL returns 200/404 with the real DB — home 135 KB, about 61 KB, contact
  50 KB, portfolio list 36 KB, blog list 45 KB, login 12 KB, admin login 8 KB,
  proposal `/proposal/divar/` 200, portfolio/blog/service details 200 — with
  no leaked `[[ ]]` markers and zero CDN references; login GET carries CSRF +
  the `next` hidden input, a bad POST re-renders the Persian error alert, and
  the proposal renders client name/intro/CTA. Structural greps over the LIVE
  templates only (404/base/blog v2/components v2/contact/core/home/partials/
  portfolio/logins): no `px-page`/`border-line`/`text-ink-dim`/`bg-paper-soft`/
  `font-display`/`font-mono`/`bg-night`/`text-lime`/`bg-lime`/
  `data-reveal="fade-up"` and no removed custom classes (`.proposal-hero`,
  `.tag-line`, `.lede`, `.site-chip`, `.section-head`, `.wordmark-link`);
  every `{% block %}` used is one base.html defines; every `{% include %}`
  resolves; all 38 `{% icon %}` names exist in
  `static/icons/lucide.sprite.svg` (85 symbols — the sprite's ids are prefixed
  `i-`, so grep for `id="i-<name>"`). **The dead classes survive only in
  unreferenced files** — the ten blog `detail_*`/`sidebar_*` partials,
  `home/sections/_manifesto.html` + `_works.html` (keys removed from
  `HomeSection` in D19) and the v1 `components/` + `components/cards/` — which
  is exactly T43's deletion list; the scratch file
  `templates/_t_cycle.html` (an untracked `{% cycle %}` probe from D30) was
  deleted. **Services list/detail are the exception and are documented under
  `## Pending pages`** — still on v1 templates and unstyled, which is T42's
  scope, not T41's.

- **D46 — Services placeholders (T42).** Confirmed broken first, as the task
  requires: none of the v1 utilities those pages were built from (`px-page`,
  `border-line`, `text-ink-dim`, `bg-paper-soft`, `font-display`, `font-mono`,
  `text-ink-soft`, `data-reveal="fade-up"` + the `stagger` filter, `bg-night`,
  `text-lime`, `btn-ink`…) exist in the compiled `static/css/tailwind.css`,
  so they returned 200 but effectively unstyled. Both were replaced with
  **minimal** placeholders — deliberately NOT a redesign, per the task order —
  that extend `base.html` and render the real DB content with classes that
  already exist: list = dark hero (orbs/shard, `services` stroke watermark,
  breadcrumbs, `ServicesPageSection` title through `highlight` + description,
  «N خدمت» chip) over a `bg-ink2` archive of icon-ring + title + excerpt +
  `s-chip` tags + arrow rows (the portfolio-list rhythm), with the
  «در حال حاضر خدمتی ثبت نشده است.» empty state; detail = dark hero (icon,
  tag chips, `highlight` title, excerpt, «مشاوره رایگان» + «مشاهده قیمت‌ها»
  buttons) then, each `{% if %}`-guarded, stats (`stat-card`/`stat-num`),
  description (`.prose-ink`), deliverables/process (two `glass-light` cards),
  why-us (`glass` grid), pricing (`glass-light` plan cards + the custom-plan
  calculator), `{% testimonials_slider service=service %}` (the D31 component
  — this is the "components must accept a service" requirement, exercised for
  the first time on a real page), FAQ (the home `.faq-item`/`.faq-q`/`.faq-a`
  markup so `pixoria.js`'s `initFaq` drives it unchanged) and other-services
  rows. The calculator kept its logic but moved to `data-*` hooks
  (`data-custom-root`/`-price`/`-total`) with a tiny Persian-digit converter,
  so no v1 class or element id survives. Views cleaned of the two now-dead
  context entries the v1 templates needed (`services_with_delay`,
  `contact_url` — the new templates `{% url %}` directly) plus the unused
  `testimonials` entry (the slider tag queries itself, D31) and `reverse`
  import; `plans` gained `prefetch_related("features")` since the template
  loops `plan.features.all`.
  **Verified:** `manage.py check` + `makemigrations --check` clean; list 200
  (42 KB) and detail 200 (73 KB) with the data-rich service
  (`/services/web-design/` — all ten sections present), 200 for a bare
  service (hero + description + other services only, optional sections fully
  skipped), 404 on a missing slug, and with an EMPTY database (rolled-back
  transaction) the list still returns 200 (22 KB) with the empty message
  visible; no v1 classes, no CDN, `crumbs` breadcrumb trail intact.

- **D47 — Lead-form section removed (T45).** The home-page quick-contact
  section is gone entirely; `/contact/` (`apps.contact`) is the only contact
  path now. Removed: the `contact` `HomeSection` key (KEY_CHOICES + seed maps
  `RENDERED_SECTIONS`/`SECTION_ORDER`/`SECTION_TITLES` + the `seed_contact()`
  method + the seed's `ContactSection` import), the `home:lead` URL, the
  `lead` view with its honeypot + `cache`-based rate limit
  (`LEAD_RATE_LIMIT`/`_lead_rate_key`/`_lead_context` and the now-unused
  `cache`/`never_cache`/`require_POST` imports), the `contact_section`/
  `contact_services`/`contact_url` home-view context entries, the
  `ContactSection` and `HomeLead` models, their admin registrations and the
  three partials (`_contact.html`, `_lead_form.html`, `_lead_success.html`).
  `apps.contact` was not touched — `ContactSubmission` and its rate limit
  stay. The `.field`/`.field-err` CSS stays: `contact/_contact_form.html` and
  `registration/login.html` still use it. The hero's default
  `cta_primary_url="#contact"` still resolves because the footer keeps
  `id="contact"` (D13). Migration `0011_remove_lead_form` does it in the
  order the task demands — RunPython deletes the `contact` HomeSection row
  FIRST (otherwise `home/index.html`'s section loop raises
  TemplateDoesNotExist for the deleted partial), then `AlterField` drops the
  key from `KEY_CHOICES`, then `DeleteModel` for both models; the reverse
  direction is a documented noop because the models no longer exist.
  Verified: `manage.py check` + `makemigrations --check` clean, `0011`
  applied (the `home_homelead`/`home_contactsection` tables are dropped and
  the `contact` section row is gone), `/` renders 200 (130 KB) with no
  lead-form markup and no `TemplateDoesNotExist`, and about/contact/portfolio/
  blog are unaffected.

- **D48 — Hero 3D fixes (T46).** `static/js/hero-scene.js`:
  **(a) one planet-offset constant.** `PLANET_X = -3.0` (was the inline magic
  `-2.0`) is now the single source of the desktop composition: `layout()` puts
  the crystal-planet group (rings and moons are children, so they travel with
  it) at `PLANET_X` on desktop and centered/raised at mobile, and the camera is
  derived from it — `camera.position.x = cur.ry * 1.2 - planet.position.x *
  0.22` (camera sits opposite the offset) with `lookAt(planet.x * 0.4 * …)`
  (reduced from 0.55 so the planet actually reads further left instead of the
  camera following it and cancelling the shift). The mobile layout keeps
  `planet.x = 0` and the same formula yields a centered planet.
  **(b) ~30% fewer stars** per layer: 900/520/240 → 630/360/168.
  **(c) the star pop is fixed — everything GPU-side.** The per-frame JS loop
  over every star (the old code rewrote ~1660 z-values per frame and re-uploaded
  three position buffers) is GONE. `PointsMaterial.onBeforeCompile` now injects,
  into three's confirmed `points_vert`/`points_frag` chunks (injection points
  verified verbatim in the local `three.module.js`: `#include <begin_vertex>`,
  `#include <project_vertex>`, `vec4 diffuseColor = vec4( diffuse, opacity );`):
  a `aPhase` attribute (per-star random phase), `mod()` z-drift + wrap inside
  the layer band, a `smoothstep` fade across BOTH wrap edges (9 units) so a
  star never appears/vanishes at full opacity, a distance fade in view space
  (`smoothstep(7,20)` close, `smoothstep(62,92)` far) and a gentle eased-sin
  twinkle (`0.6 + 0.4·sin(t·1.6 + phase·1.7)`, never zero) — combined into
  `vAlpha` which multiplies the fragment alpha. No hard thresholds anywhere.
  Per frame the CPU now writes ONE shared clock value + one speed per layer
  (`speed * layer.speedMul * 14` preserves the old drift velocity). Two
  robustness guards came with it: animation time moved from `clock.elapsedTime`
  to a clamped `starTime` accumulator (a long pause can no longer teleport the
  stars, and the time survives loop restarts — `clock.start()` used to reset
  it), and the render call is wrapped in try/catch that stops the loop and
  raises `#hero-fallback` on any runtime/shader failure, extending D17's
  "any failure falls back" promise to failures that surface mid-loop.
  NOT verified in a browser (no Playwright/Puppeteer in the project; the shader
  was reviewed by hand against the local three source and the module passes
  `node --input-type=module --check`); the home page still renders 200 and
  loads the module.

- **D49 — Shared breadcrumb component (T47).** `templates/components/
  _breadcrumb.html` is now the single breadcrumb renderer: props `crumbs`
  (from the existing `apps/core.context_utils.crumbs`) and `theme`
  (`"dark"`/`"light"` — every current hero is `bg-ink`, so all callers use the
  default dark variant; the light variant exists for the cream sections future
  pages may add). It renders nothing when `crumbs` is empty, so a page without
  a trail emits zero characters. The five identical inline `<nav>` blocks
  (blog list/detail, services list/detail, portfolio detail — all the same
  markup modulo `truncatechars`) were replaced with one `{% include %}`, and
  three pages that built a `crumbs` trail in the view but never rendered it
  now show it: `portfolio/list.html`, `core/about.html`, `contact/contact.html`
  (each wrapped in a `mb-5` spacer above the eyebrow), plus `404.html` —
  `config.views.custom_404` now passes `crumbs(("خانه", "home:home"), ("خطای
  ۴۰۴", None))` and the centered hero wraps the include in a
  `flex justify-center` (verified through `handler404` with `DEBUG=False`).
  The old helper's docstring was updated to point at the component.
  The component also raised the bar the task asked for: `text-sm` mobile /
  `md:text-base` desktop (was a tiny `font-latin text-[10px] tracking-[.3em]`
  that styled Persian text with the latin font), better contrast
  (`text-cream/70` links, `text-cream` + `font-medium` current page, was
  `/40` and `/70`), comfortable tap targets (`rounded px-1.5 py-1` on every
  link/span), an RTL separator that actually points left — the local
  `chevron-left` Lucide sprite instead of the old rotated gold square — and
  `aria-label` + `aria-current="page"` kept.
  **GOTCHA, caught by rendering the page:** the new file's header comment was
  a multi-line `{# … #}` block, and per the template-lexer GOTCHA above the
  whole comment LEAKED into the rendered HTML (the lexer's `{#.*?#}` has no
  DOTALL, so an unmatched `{#` is just text). Caught by dumping the rendered
  `/about/` markup, fixed by switching to `{% comment %}…{% endcomment %}` —
  the same rule every other partial in this project already follows.
  Verified: every list/detail page renders exactly one breadcrumb `<nav>` with
  exactly one `aria-current`, the trail shows home → parent → current with
  chevron separators, `manage.py check` + `makemigrations --check` clean, and
  Tailwind was rebuilt for the new utilities (`text-ink/70`, `text-gold/80`,
  `md:text-base`, `md:h-4`, `h-3.5`).

- **D40 — Blog model review + prose styles (T38).** The model layer was
  already nearly complete for the v2 pages; the review added only the missing
  pieces, all optional so a bare article still renders: `Article.featured`
  (bool, seeds the hero slot of the list page — T39), and `cover_image` +
  `cover_image_alt` became **blank=True** with a new `get_cover_alt()` helper
  (fallback to the title, mirroring `Portfolio.image_alt`) so an article can
  be saved without a cover at all and the alt text is never empty — D37 found
  the same a11y gap in the portfolio model. `BlogPageSettings` gained
  `eyebrow` (every v2 section header has one) plus the `[[ ]]` `help_text` on
  `title`, and the commented-out `title_highlight` remnant was deleted — the
  `highlight` filter replaces it (D2). Migrations `blog.0004` (featured +
  eyebrow + title help_text) and `0005` (cover fields blank). Admin:
  `featured` joined `list_display` + `list_editable` (next to `status`),
  `list_filter` gained `featured`/`author`, `search_fields` gained
  `meta_title`, `prepopulated_fields` for the slug, `BlogPageSettings` got a
  fieldset with the marker description, Tag/Author got `search_fields`. Seed:
  `apps/blog/management/commands/seed_blog_content.py` — the D25 pattern once
  more: `first_or_create` for the singleton (only fills `eyebrow` when empty —
  the existing row holds the user's real title/description) plus a one-time
  `featured` pick of the newest published article when NO article is featured
  yet (never moves a flag the admin already set). Two runs are clean no-ops
  (verified). The command deliberately touches NO article content — blog
  posts are the user's own writing, like portfolio projects (D37).
  **The reusable rich-text style is `.prose-ink` / `.prose-cream`** in
  `static/src/input.css`: two variants of one system for TinyMCE `HTMLField`
  output, ink for light (cream) backgrounds and cream for dark, covering
  every tag the TinyMCE toolbar can emit — h2 (with a short gold dash above,
  matching `.eyebrow`'s visual language) through h6, p, strong/em/u/s, links
  (gold underline, offset 4px, hover deepens), `ul` with rotated-square gold
  markers (list-style none + `::before`), `ol` with circled Persian counters
  (`counter(ol-counter, persian)` — the browser renders ۱/۲/۳ natively),
  blockquote with a 3px gold RIGHT border (RTL — a left border would read
  backwards), inline + block code (Space Grotesk via `--font-latin`,
  `direction: ltr` + `unicode-bidi: isolate` so a Latin snippet inside RTL
  prose is never re-shaped), tables (right-aligned headers, `display: block`
  + `overflow-x: auto` on narrow screens), `figure`/`figcaption`, and `hr` as
  a gold gradient fade. RTL is baked in everywhere (padding-right on lists,
  right-side markers and borders, right text-align in table cells). The
  portfolio detail page (T37) was migrated from its inline arbitrary
  variants to `.prose-ink` for description/challenge/solution, and the blog
  detail body (`detail_body.html`) got it too, so the style is exercised by
  two pages already. **Verified:** `manage.py check` + `makemigrations --check`
  clean, every admin page (changelist/add/change/settings) 200, blog detail
  200 with a rich fixture (all tags render, TOC `toc-N` ids intact, sidebar
  links resolve), 200 with a cover-less article (cover section skips), list
  200, all other pages unaffected, Tailwind rebuilt (73 prose rules
  compiled). No visual regression tool exists in this repo, so the CSS was
  verified structurally (compiled output + selector coverage) rather than by
  screenshot.

- **D41 — Blog list page (T39).** `templates/blog/list.html` rebuilt on
  `base.html` in the D27 language, mirroring the portfolio list page's
  rhythm: a dark `bg-ink` hero (mouse-parallax orbs/shard, `blog` stroke
  watermark, breadcrumb trail, `eyebrow` + `highlight` title + description
  from `BlogPageSettings`, «N مقاله · M دسته‌بندی» chip row) followed by a
  `bg-ink2` archive with an ink-filled `divider-flip` wave. New pieces:
  **(a) a featured-article slot** at the top of the archive — a wide
  `glass tilt` split card (cover image left, content right, `blog-chip`
  «ویژه» badge) driven by the `Article.featured` flag added in T38. The view
  picks the newest published featured article; when none is flagged the slot
  is skipped entirely. The featured article is NOT excluded from the paginated
  grid — it sits in the archive too, and the slot is a curation highlight, not
  a separate list. Verified: its link appears exactly once in the page.
  **(b) the filter row kept HTMX** (unlike the portfolio list, whose filter is
  pure client-side): the pills are the shared `.flt-btn` component, each with
  `hx-get`/`hx-target="#blog-grid"`/`hx-swap="innerHTML"`, so clicking a
  category replaces the grid server-side. The `aria-pressed` sync script moved
  from a v1 `filter-btn` listener to `.flt-btn` and now also toggles the
  `.active` class (the v1 styled via `aria-pressed` variants; v2's `.flt-btn`
  uses `.active`). **(c) `blog/partials/article_cards.html` and
  `load_response.html` now render `components/_article_card.html`** with a
  per-card `{% cycle %}` delay (the D30 gotcha — `cycle` inside an include
  resets, so the caller generates the stagger), replacing the v1
  `components/cards/blog_card.html`. The `{% empty %}` branch renders a
  centered «مقاله‌ای در این دسته منتشر نشده است.» — both on the initial
  page and inside the HTMX response. **(d) reveal/tilt after HTMX — the real
  fix.** `pixoria.js` ran `gsap.from(...)` over a `querySelectorAll`
  snapshot at boot, so load-more cards arrived already-visible with no
  animation. Two initializers were factored out (`revealEl`, `tiltCard`), and
  an `htmx:afterSettle` listener now re-runs them **only** on elements tagged
  `data-blog-reveal` (marked on every card by the partial via a new
  `data_blog_reveal` prop on `_article_card.html`), with a
  `data-reveal-done` guard so a second swap can't double-animate a card.
  Reduced-motion and touch are respected (tilt is skipped on touch). No new
  CSS was needed — every class (`glass`, `tilt`, `glare`, `blog-card`,
  `blog-chip`, `flt-btn`, `eyebrow`, `stroke-title`, `divider-flip`,
  `grid-bg`, `orb`, `shard`) already existed. **Search was deliberately NOT
  added** — the view has no search support and the task says only if already
  supported. Verified: list 200 (47 KB) with featured slot + filter + 3-col
  grid; `blog:load` page 2 returns cards each carrying
  `data-blog-reveal` + an OOB `load-more-wrapper` swap; a category with no
  articles renders the empty message; an EMPTY database (no articles, no
  categories) renders 200 with the featured slot and filter row skipped and
  the empty message visible; home/about/contact/portfolio unaffected; node
  module syntax check passes; Tailwind rebuilt (no token changes).

- **D38 — Portfolio list page (T36).** `templates/portfolio/list.html` rebuilt
  on `base.html` in the D27 design language: a dark `bg-ink` hero (orbs/shard
  with `data-mouse-parallax`, a stroked latin `works` watermark, `eyebrow` +
  `highlight` h1 + description from the `PortfolioPageSection` singleton, and a
  «N پروژه · M دسته‌بندی» chip row) followed by a `bg-ink2` archive section
  with an ink-filled `divider-flip` wave, the same `flt-btn` filter pills the
  home section uses, the latin «N PROJECTS» counter, and a 3-column grid of
  `_project_card.html` (radius `{% cycle %}` exactly like home). No new CSS —
  every class (`eyebrow`, `stroke-title`, `divider`, `grid-bg`, `orb`, `shard`,
  `tile`, `flt-btn`, `font-latin`) already existed. CTA/footer come from base.
  **Filter is client-side**, matching the home section: the view now passes
  *all* projects (`prefetch_related("categories")`, ordered by `order`/`id`)
  and `?category=<slug>` only sets the initially-active pill — an invalid slug
  no longer 404s the whole archive (the old `get_object_or_404` did). The old
  `portfolios_with_delay` context entry (a v1 stagger helper) is gone; the
  cards animate via the filter itself. **No pagination/load-more by design:**
  a JS filter and server-side paging fight each other (paged-in cards would
  need `data-cat` re-application), the home precedent is all-items + filter,
  and a studio archive is a few dozen projects at most — add a cap +
  `blog:load`-style HTMX later only if the archive actually grows.
  **The filter component was generalized** (the D26 rule): `pixoria.js`'s
  `initPortfolioFilter` no longer reads the hard-coded `#pf-grid`/`#pf-filters`
  /`#pf-count`/`#pf-empty` ids — it loops `document.querySelectorAll("[data-
  pf-root]")` and looks each part up inside that root, so several filters can
  share a page. Two behaviours were added behind the opt-in `data-pf-sync`
  attribute (archive only, home behaviour unchanged): the URL is kept in sync
  with `history.replaceState` on every filter click, and a `?category=` on load
  pre-selects its pill. `home/sections/_portfolio.html` migrated to the same
  hooks (`id="pf-*"` → `data-pf-*`), so the two pages are one component.
  Verified: list 200 (37 KB) with both projects, `?category=web-design`
  pre-selects its pill, `?category=nope` still 200, empty DB (no projects, no
  categories) renders 200 with 0 cards, 0 pills and the «پروژه‌ای ثبت نشده
  است.» message visible by default; home unchanged (hooks present, no old
  ids); no leaked `[[ ]]`, zero CDN refs; `node --check` on the module passes;
  Tailwind rebuilt (no token changes).

- **D37 — Portfolio model review (T35).** The review found the model layer
  already covered the planned pages; the missing pieces were added, all
  optional so a bare project still renders: `image_alt` (a11y/SEO for the
  cover), `technologies` csv + `get_technologies_list()` (mirrors
  `Service.get_chips_list()`), a nullable `testimonial` FK to
  `services.ServiceTestimonial` (the detail page's optional customer-quote
  card — the component `testimonials_slider` needs a `service`, so the detail
  page renders this one card directly instead), `meta_description` +
  `get_meta_description()` (fallback to `excerpt`, mirrors `Article`), an
  `icon` on `ProjectStat` (validated by `validate_icon_name`, previewed in the
  inline via `IconPreviewMixin`), a new `ProjectImage` child
  (`image`/`alt`/`caption`/`order`, `related_name="gallery"`) rendered only
  when present, and `eyebrow` on `PortfolioPageSection` with `[[ ]]`
  `help_text` on both titles. Migration `portfolio.0004`; admin gained
  fieldsets (تصویر و گالری / مشتری و دسته‌بندی / محتوای پروژه / بازخورد و سئو /
  نمایش), the `ProjectImageInline`, `list_filter` (`categories`, `featured`),
  `search_fields` and the icon preview column.
  Seed: `apps/portfolio/management/commands/seed_portfolio_content.py` (new
  management package in the portfolio app). It deliberately touches NO project
  data — نمونه‌کارها are the user's real client work, so stats/gallery/
  technologies stay admin-entered (unlike home/about, whose copy is the
  design's prose). It only fills the section `eyebrow` when empty («نمونه‌کارها»,
  matching the home portfolio section's eyebrow) and creates the four default
  `Category` rows only when the table is completely empty, so a fresh DB has a
  working filter and an existing one is never clobbered. Two runs are clean
  no-ops (verified). Verified: `manage.py check` + `makemigrations --check`
  clean; `/portfolio/` and a detail page render 200 with data, `/portfolio/`
  still 200 with an empty project table and a missing slug 404s; every admin
  page (changelist/add/change) renders 200; an invalid icon name is rejected
  and a valid one saves. Verified end to end after the two throwaway rows
  (one `ProjectStat`, one `ProjectImage`) from the icon/gallery check were
  removed again.

- **D36 — Contact page template (T34).** `templates/contact/contact.html` fully
  replaced (v1 page-hero + project-type/budget/start-time selects out) with the
  four `new/contact.html` sections on top of `base.html`: hero → form →
  cities/map → FAQ, then the shared `_cta.html`/`_footer.html` — ~1800 lines of
  duplicated chrome from the prototype dropped. The header, mobile menu, CTA
  and footer are base's; no hard-coded copy of them survives. Conversions:
  `[[ ]]` titles via `highlight` (dark variant on the cream sections), all
  `data-lucide` → the local `{% icon %}` sprite, phone digits via `fa_digits`,
  decorative `hello` stroke via the existing `.stroke-title`. The hero's four
  contact cards render from `SiteSettings` (phone / phone_secondary / email /
  website — the same single source the header/footer use, so the vestigial v1
  `ContactInfo` model stays untouched for T43), each card `{% if %}`-guarded and
  its rotating border-radius + `lg:mt-10` offset generated with two `{% cycle %}`
  tags in lockstep. The form column's points come from `ContactFormPoint`, the
  `.soc` buttons from `SocialLink` (with `|default:"globe"` like the footer),
  and the FAQ uses the home `.faq-item`/`.faq-q`/`.faq-a` markup so
  `pixoria.js`'s `initFaq` drives it unchanged — the prototype's own accordion
  classes are gone. The radial map SVG is ported verbatim with its labels bound
  to `ContactMapSection` (`office_name`/`office_note`/`coverage_note`), keeping
  the SMIL animations (`cities-spin` classes already existed in `input.css`).
  JSON-LD (Organization + ContactPage + BreadcrumbList) moved into `extra_head`.
  The form itself is `templates/contact/_contact_form.html` (built earlier with
  the `.field`/`.field-err` styles) included into the page, and htmx swaps its
  `outerHTML` with either itself (validation errors / rate-limit alert) or the
  new `templates/contact/_contact_success.html`, which carries the hidden
  `[data-toast]` span so `pixoria.js` announces the success message after
  `htmx:afterSettle` (D16) and offers an «ارسال پیام دیگر» link back to the
  same page. Verified end to end: GET 200 (54 KB) with all four sections, no
  leaked `[[ ]]`, zero CDN/lucide references; a valid POST creates exactly one
  `ContactSubmission` (name/email/phone/subject/message) and returns the success
  card; an invalid POST re-renders the form with the Persian `field-err`
  messages; the honeypot returns the success card and saves nothing; the
  `cache`-based rate limit lets exactly `RATE_LIMIT` (5) rows through and blocks
  the 6th with the alert; and with an EMPTY database (rolled-back transaction)
  the page still returns 200 (28 KB) — hero/map/FAQ `{% if %}`-skip while the
  form still validates. Home (146 KB) and about (65 KB) unaffected. Tailwind
  rebuilt (no token changes — just the newly-used `sm:grid-cols-2` / `lg:mt-10`
  utilities).

- **D42 — Blog detail page (T40).** `templates/blog/detail.html` rebuilt as
  one self-contained file on `base.html` (the D39 portfolio-detail precedent),
  so the seven v1 partials it used to include (`detail_hero`/`detail_cover`/
  `detail_body`/`sidebar_toc`/`sidebar_author`/`sidebar_related`/`sidebar_cta`/
  `detail_related_section`/`detail_post_nav`/`detail_cta`) are now unreferenced
  and left for T43 — they still carry the dead v1 tokens (`text-ink-dim`,
  `bg-paper-soft`, `border-line`, `text-lime`, `bg-night`, `px-page`) and
  rendered unstyled. Four sections in the v2 rhythm: hero (`bg-ink`,
  mouse-parallax orbs/shard, latin `article` stroke watermark, breadcrumb trail
  ending on the article title with `truncatechars:34`, category chip →
  `blog:list` + `#tag` chips, `highlight` h1, excerpt, four glass meta tiles —
  author / Jalali publication date (`fa_jdate`) / reading time (`fa_digits`) /
  updated-at (`is_updated()`, `sparkles` icon); tile border-radii are literals,
  not `cycle`, because each tile renders exactly once) → cover (`bg-ink2`,
  `divider-flip` fill `#0a0a0c`, `fetchpriority="high"`, skipped when
  `cover_image` is empty) → body (`bg-cream`, `border-radius: 3rem 9rem 0 0`,
  `lg:grid-cols-12`: `prose-ink` article with an excerpt lead, the TOC-id'd
  content and the share bar, plus a sticky `glass-light` sidebar — TOC, author
  card (`.avatar` with `initial()` fallback) and an ink consultation card whose
  copy is the v1 prose) → related (`bg-ink2`, divider fill `#f5f3ee`, header +
  `{% articles_carousel exclude=article category=article.category limit=6 %}`
  + prev/next glass cards). **The view's `related_articles` slice became
  `has_related`**, a `.exists()` mirroring the carousel's own query
  (`published` + same category + excluding the article), so the header never
  renders over an empty track; prev/next keep their own `published_at`
  queries and their own `{% if prev_article or next_article %}` guard inside
  the section. The crumbs' last item is now the article title (was the
  *category* title, which duplicated the chip row and never marked the page).
  **All page JS moved into pixoria.js** as `initArticleChrome()` — the
  template's `extra_js` block is gone entirely: (a) the reading-progress bar
  reads `[data-reading-progress]` (the `<article>`) and scales `[data-reading-
  bar]` (origin-right gold gradient) from plain scroll geometry, no GSAP
  needed; (b) the TOC active link resolves each `[data-toc-link]`'s target with
  `CSS.escape` + IntersectionObserver (`rootMargin: -20% 0px -70% 0px`) and
  toggles `.active`, styled with self-referential arbitrary variants
  (`[&.active]:bg-gold/10`, `group-[.active]:bg-gold-dark`) so no new CSS was
  needed for it; (c) `[data-copy-link]` swaps its `data-copy-default` /
  `data-copy-done` spans for 2s and falls back to `pixoriaToast` when the
  Clipboard API is missing or rejects. No element ids anywhere on the page.
  Share buttons: x / LinkedIn / Telegram are plain intent links and the fourth
  is the copy button, all `.share-btn` (the one new CSS class, next to
  `.blog-chip`). JSON-LD (`BlogPosting` + `BreadcrumbList`) in `extra_head`
  via the `json` filter, with the conditional `image`/`author` placed *before*
  the unconditional `publisher` so the trailing commas can never break the
  script. **Icon gotcha:** the design-adjacent names `hash` (tag chips) and
  `refresh-cw` (updated tile) are NOT in the local sprite — tags use a literal
  gold `#` and the tile uses `sparkles`; check `static/icons/lucide.sprite.svg`
  before naming an icon (D3). Verified: detail 200 (58 KB) with cover/TOC
  (4 h2 → 4 entries)/tags/share/carousel/prev-next; 200 for the only article
  in its category (whole related section — header, carousel and nav — hidden);
  200 with cover/author/tags stripped (own cover section and the JSON-LD
  `image`/`author` keys gone, related cards keep their covers); 200 with an
  empty DB (no TOC, no related, no author card, share bar stays); 200 for a
  rich fixture (3 TOC entries, author in JSON-LD and sidebar); missing slug
  404; JSON-LD parses; home/about/contact/blog-list/portfolio-list unchanged;
  `manage.py check` + `makemigrations --check` clean; node module check passes;
  Tailwind rebuilt (no token changes — the two arbitrary variants compiled).

- **D50 — Template-comment leak sweep (T47b).** Three home partials still
  carried the multi-line `{# … #}` pattern the D49 GOTCHA warns about, so their
  whole comment block rendered as literal text in the page (verified by
  rendering `/`: the `{# … #}` string was present in the response body).
  `templates/home/sections/_portfolio.html` and `_stats.html` were already
  converted to `{% comment %}…{% endcomment %}` in the working tree (uncommitted
  — the report came from a cached page / the 2026-10-05 screenshot); the last
  live leak was `templates/home/sections/_trusted.html:24`. All three are now
  `{% comment %}` blocks. Confirmed against Django 5.2's actual lexer
  (`tag_re = re.compile(r"({%.*?%}|{{.*?}}|{#.*?#})")` — **no** `re.DOTALL`, so
  `{#.*?#}` can never span a newline) and verified by re-rendering: `/`, `/about/`,
  `/contact/`, `/portfolio/`, `/blog/` all contain zero `{#` / `{% comment %}`
  markers (home 130646 → 130517 bytes). A repo-wide scan for any remaining
  `{#` without a same-line `#}` (the exact leak condition) now returns zero
  hits. Rule stands: multi-line template notes use `{% comment %}`.

- **D51 — Labeled dual phone numbers (T48).** `SiteSettings.phone_label`
  (default «دفتر مرکزی») and `phone_secondary_label` (default «پشتیبانی»), both
  blank-allowed, migration `core.0010` (already applied to the live DB). The two
  rules from the task: DISPLAYED digits go through `|fa_digits` (Persian),
  `tel:` hrefs and JSON-LD keep LATIN digits — verified by rendering every page
  (`tel:` hrefs contain no Persian digit; no `fa-num` span shows a latin digit).
  Wiring: the footer shows both numbers with their label as a small sub-line,
  the CTA section gained the second phone next to the mailto link (with its
  label in parentheses), the mobile menu gained the second phone, and the
  contact-page hero cards show icon + label + big gold number for each. The
  header shows NO phone on desktop (only the mobile overlay), so nothing was
  added there — the task's "if it shows a phone" clause. JSON-LD: one new
  shared partial `templates/partials/_json_telephone.html` emits
  `"telephone": ["…", "…"],` (all non-empty SiteSettings numbers, nothing when
  none are set) and is included by `home/index.html`, `core/about.html` and
  `contact/contact.html`. **Bug fixed in this session:** `home/index.html` had
  the include on the Organization node AND a leftover single-string
  `"telephone": "{{ settings.phone }}",` on its ContactPoint node — the same
  key twice, once a list and once a string; the ContactPoint now uses the same
  partial. `seed_home_content` now seeds latin-digit phones + both labels (it
  only touches a fresh DB — the live row holds the user's real content
  `09011016263` / empty secondary and was NOT touched, per the D25 rule).
  Verified: `manage.py check` + `makemigrations --check` clean; `/`, `/about/`,
  `/contact/`, `/portfolio/`, `/blog/` all 200 with 3–4 latin `tel:` hrefs and
  list-form `telephone` in every JSON-LD.

- **D52 — Category typo fix (T49).** The only occurrence of «سیات» in the whole
  project was one live DB row: `portfolio.Category` id=1 `name='طراحی سیات'`
  (shown before editing). NO source file, seed command, fixture or JS contained
  it (repo-wide grep + a raw-SQL scan of every table/column), so nothing in the
  code needed changing. The slug was already the correct latin `web-design`, so
  per the task it was left untouched — `/portfolio/?category=web-design`, the
  filter pills and every `category.filter_url` link keep working with no
  redirect needed. Fixed with a proper idempotent data migration,
  `portfolio.0005_fix_web_design_category_typo` (a `RunPython` that only
  rewrites rows still named exactly «طراحی سیات»; reverse is a documented
  no-op). Verified: name is now «طراحی سایت» with the slug unchanged, the
  migration survives an unapply/reapply round-trip as a no-op, and the filter
  pills on `/` and `/portfolio/` read «طراحی سایت» with zero remaining «سیات»
  in either rendered page. `manage.py check` + `makemigrations --check` clean.

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
- [x] T29 — Testimonials SECTION component: inclusion tag
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
- [x] T30 — Generic carousel component + CAROUSEL SECTIONS:
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

- [x] T31 — Extend about models for the v2 about page (hero, story,
  journey/timeline, stats, values, team, clients wall, CTA — whatever exists
  in `new/about.html`), reuse existing `core.About*` models and `TeamMember`;
  add only what is missing; migration + admin (Persian
  help_text/verbose_name, inlines, `order`, `is_active`); optional-content
  rules; seed command with the original Persian copy from `new/about.html`
  (idempotent, no overwriting) |
  files: `apps/core/models.py`, `apps/core/migrations/0009_*`, `apps/core/admin.py`,
  `apps/core/management/commands/seed_about_content.py`, `apps/core/views.py` |
  commit: "feat(about): add v2 about page models"
- [x] T32 — Rebuild `templates/core/about.html` from `new/about.html`: extend
  `base.html`, REMOVE the duplicated hard-coded header/footer/CTA from the new
  file (base ones are the reference), bind everything to the models, use
  `highlight` for colored words, `{% icon %}` for icons, `fa_digits`/counters
  where needed, local JS only, skip empty sections. Update `apps/core/views.py`
  | files: `templates/core/about.html`, `apps/core/views.py`,
  `apps/core/models.py` (`AboutStory.get_chips_list`),
  `templates/home/sections/_hero.html` (`data-mouse-parallax` hook),
  `static/js/pixoria.js` (parallax generalized) |
  commit: "feat(about): rebuild about page in v2 style"

### Phase 7 — Contact page (from `new/contact.html`)

- [x] T33 — Extend contact models for v2 (info cards, subject/project-type/
  budget/start-time choices, FAQ, cities/map block, working hours, socials)
  reusing existing `contact.*` models; migration + admin + seed (same rules) |
  files: `apps/contact/models.py`,
  `apps/contact/migrations/0003_*`, `apps/contact/admin.py`,
  `apps/contact/management/commands/seed_contact_content.py` |
  commit: "feat(contact): add v2 contact models"
- [x] T34 — Rebuild `templates/contact/contact.html` from `new/contact.html`:
  extends `base.html`, no duplicated header/footer/CTA, working form (Django
  form/model, saved `ContactSubmission` visible in admin, CSRF, validation
  with Persian error/success messages, honeypot + simple rate limit like the
  home lead form, HTMX with `data-toast` success announcement per D16,
  optional email notification only if email settings already exist). Reuse the
  `.field` styles from `static/src/input.css` |
  files: `templates/contact/contact.html`, `apps/contact/views.py` |
  commit: "feat(contact): rebuild contact page with working form"

### Phase 8 — Portfolio pages (no design in `new/`: design them)

- [x] T35 — Review `portfolio` models vs the planned pages; add only what is
  missing (e.g. optional gallery images inline, results/metrics via existing
  `ProjectStat`, technologies/tags, optional related testimonial link, SEO
  fields), all optional; migration + admin + seed if needed |
  files: `apps/portfolio/models.py`, `apps/portfolio/migrations/`,
  `apps/portfolio/admin.py` | commit: "feat(portfolio): extend models for v2 pages"
- [x] T36 — Portfolio LIST page `templates/portfolio/list.html`: v2 hero
  (eyebrow + `highlight` title from admin-editable settings if reasonable),
  category filter (server-side by existing URL/query if the view supports it,
  else JS filter), 3-column grid using `_project_card.html`, pagination or
  HTMX load-more, empty state, CTA from base |
  files: `templates/portfolio/list.html`, `apps/portfolio/views.py` |
  commit: "feat(portfolio): rebuild list page in v2 style"
- [x] T37 — Portfolio DETAIL page `templates/portfolio/detail.html`: hero with
  cover image, meta (client, year, service type, categories, external link),
  challenge/solution sections, stats counters (`ProjectStat`, now with `icon`),
  gallery if present, description (rich text styled), next/previous project,
  `{% projects_carousel exclude=object %}` as related projects, optional
  `{% testimonials_slider service=... %}` only if it makes sense. JSON-LD +
  meta blocks | files: `templates/portfolio/detail.html`,
  `apps/portfolio/views.py` | commit: "feat(portfolio): rebuild detail page in v2 style"

### Phase 9 — Blog pages (no design in `new/`: design them)

- [x] T38 — Review `blog` models; add only what is missing (featured flag,
  optional cover alt text — SEO fields exist already); migration + admin if
  needed. Add a reusable rich-text typography style for TinyMCE `HTMLField`
  content in `static/src/input.css` (headings, lists, quotes, images, tables,
  code, links) in the gold/cream/ink language, RTL-correct |
  files: `apps/blog/models.py`, `apps/blog/migrations/`, `apps/blog/admin.py`,
  `static/src/input.css`, `apps/blog/management/commands/seed_blog_content.py` |
  commit: "feat(blog): extend models and add prose styles"
- [x] T39 — Blog LIST page `templates/blog/list.html`: v2 hero, featured
  article, category filter, search only if already supported by the view, grid
  using `_article_card.html`, keep the existing `blog:load` HTMX load-more
  behavior working with the new cards (update the `blog` partial used by
  `blog:load`), empty state | files: `templates/blog/list.html`,
  `templates/blog/partials/article_cards.html`,
  `templates/blog/partials/load_response.html`,
  `templates/components/_article_card.html`, `apps/blog/views.py`,
  `static/js/pixoria.js` | commit: "feat(blog): rebuild list page in v2 style"
- [x] T40 — Blog DETAIL page `templates/blog/detail.html`: hero with cover,
  category, Jalali date (`fa_jdate`), reading time (`fa_digits`), author,
  reading-progress bar, article body with the typography style, auto table of
  contents from headings only if it can be done cheaply (small local JS, no
  library), tags, share buttons (plain links, no third-party scripts),
  `{% articles_carousel exclude=article category=article.category %}` as
  related posts, Article JSON-LD, meta blocks. Keep
  `blog:tinymce-image-upload` untouched | files: `templates/blog/detail.html`,
  `apps/blog/views.py`, `static/js/pixoria.js` |
  commit: "feat(blog): rebuild detail page in v2 style"

### Phase 11 — Fixes and site-wide polish

- [x] T45 — REMOVE the home-page contact/lead-form section completely: delete
  the `contact` HomeSection key (KEY_CHOICES, data migration deleting the row,
  seed maps, `home/index.html`, view context), the `_contact.html` /
  `_lead_form.html` / `_lead_success.html` partials, the `home:lead` URL + view
  + rate-limit code, the `ContactSection` and `HomeLead` models (+ their admin,
  inline/FK references, seed code, JSON-LD/sitemap references) and any CSS/JS
  used only by it. Grep the whole repo FIRST and list every reference in this
  file. Create proper migrations (delete models only AFTER removing FKs). Do
  NOT touch `apps/contact` — the dedicated `/contact/` page and
  `ContactSubmission` stay. The hero default CTA `#contact` still lands on the
  footer (D13) | files: `apps/home/models.py`, `apps/home/migrations/`,
  `apps/home/views.py`, `apps/home/urls.py`, `apps/home/admin.py`,
  `apps/home/management/commands/seed_home_content.py`,
  `templates/home/index.html`, `templates/home/sections/_contact.html`,
  `_lead_form.html`, `_lead_success.html`, `static/src/input.css`,
  `static/js/pixoria.js` | commit: "feat(home): remove lead form section"
- [x] T46 — Hero 3D fixes (`static/js/hero-scene.js`): (a) shift the crystal
  planet (and its rings/moons group) toward the physical LEFT of the screen on
  desktop — centered or slightly offset on mobile so the text stays readable,
  with the offset as ONE constant; (b) reduce the star count by ~30% across all
  star layers; (c) fix the star pop-in/out problem (stars vanishing/reappearing
  abruptly on scroll travel, twinkle and camera movement): per-star alpha/size
  fade via a shader attribute or `PointsMaterial` + `onBeforeCompile` (fade by
  distance/near-far plane and at wrap boundaries), gentle eased-sin twinkle, no
  hard threshold toggling — GPU-side, no per-frame JS loops over thousands of
  stars. Keep every D8/D17 performance rule |
  files: `static/js/hero-scene.js` | commit: "fix(hero): shift planet left and smooth stars"
- [x] T47 — Breadcrumbs: one shared partial `templates/components/_breadcrumb.html`
  (props: list of crumbs, theme dark/light) replacing the duplicated inline
  breadcrumb markup on every page (portfolio/blog/services/about/contact/404).
  Text ≥ `text-sm` on mobile and `md:text-base` on desktop, better contrast,
  comfortable tap targets (padding), RTL separators (chevron pointing LEFT),
  `aria-label` + `aria-current="page"` |
  files: `templates/components/_breadcrumb.html`, every page with crumbs,
  `apps/core/context_utils.py` (the `crumbs` helper) |
  commit: "feat(components): shared breadcrumb partial"
- [x] T47b — Fix leaking template comments: the multi-line `{# … #}` blocks in
  `templates/home/sections/_portfolio.html`, `_stats.html` and `_trusted.html`
  rendered as literal text on the home page (the D49 lexer GOTCHA — Django's
  `tag_re` has no DOTALL). Convert all three to `{% comment %}…{% endcomment %}`
  and sweep the whole `templates/` tree for any remaining `{#` without a
  same-line `#}` | files: `templates/home/sections/_portfolio.html`,
  `templates/home/sections/_stats.html`, `templates/home/sections/_trusted.html` |
  commit: "fix(templates): stop multiline comment leak into rendered pages"
- [x] T48 — Two phone numbers: verify `SiteSettings.phone` and `phone_secondary`
  are editable in the admin with Persian labels/help_text, and add optional
  `phone_label` / `phone_secondary_label` («دفتر مرکزی» / «پشتیبانی»). The
  header (if it shows a phone), footer, CTA partial, contact page cards,
  about/contact JSON-LD (`telephone` as a LIST) and every `tel:` link must use
  BOTH numbers when set and skip an empty one. Rendered digits go through
  `fa_digits`; `tel:` hrefs keep latin digits |
  files: `apps/core/models.py`, `apps/core/migrations/`, `apps/core/admin.py`,
  `templates/partials/_footer.html`, `templates/partials/_cta.html`,
  `templates/contact/contact.html`, `templates/core/about.html` |
  commit: "feat(core): labeled dual phone numbers everywhere"
- [x] T49 — Fix the typo «طراحی سیات» → «طراحی سایت»: grep the repo (templates,
  seed commands, fixtures, models, JS), fix the SOURCE, then fix the existing
  DB row (a portfolio `Category` name/slug — show the prior value before
  editing, keep the slug stable unless it is also wrong and no redirects are
  needed). Check the portfolio filter pills on home and `/portfolio/` afterwards
  | files: seed commands + a one-time data migration/nudge |
  commit: "fix(content): correct web design category typo"
- [ ] T50 — Home portfolio responsive layout: desktop (≥lg) = 3-column grid
  (keep the filter, radius variants, empty state, D29 trimming); tablet (md) =
  carousel with 2 cards per view; mobile = carousel with 1 card per view (CSS
  scroll-snap, reusing the D32 `initCarousels` dots/prev-next + RTL keyboard).
  ONE DOM only — a single container that is a grid at `lg` and a snap-scroller
  below `lg`, no duplicated cards. The category filter must keep working in
  both modes (filtered-out cards removed with `hidden`; carousel dots and scroll
  position reset/recompute after each filter click). Page height must not grow
  on small screens. Apply the same behavior to `/portfolio/` only if it does not
  break its pagination-free filter; otherwise keep the list page a normal grid
  and record why | files: `templates/home/sections/_portfolio.html`,
  `templates/portfolio/list.html`, `static/js/pixoria.js`, `static/src/input.css` |
  commit: "feat(portfolio): responsive grid to carousel"
- [ ] T51 — Testimonials by type (text / video / audio): make the admin form
  adaptive for `ServiceTestimonial` — the `kind` select shows/hides the relevant
  fieldsets with a small admin JS file (`static/admin/js/testimonial_kind.js`
  loaded via `Media`), and `clean()` validates that the chosen kind has its
  required fields (text → quote; video → video file or URL + poster; audio →
  audio file or URL + title). Add real media fields if missing
  (`video_file`/`video_url`, `audio_file`/`audio_url`) and make the front-end
  cards REAL players, not simulations: `<video preload="none" playsinline
  controls-or-custom>` with poster, `<audio preload="none">` with the waveform
  UI driven by the real `currentTime`/`duration` (keep the pretty waveform, real
  playback state, pause the others when one starts). Duration fields become
  optional (auto-read from metadata when empty). `_testimonial_card.html` picks
  the template by `kind`; `testimonials_slider` includes every kind
  automatically. Persian help_texts. Verify with one fixture of each kind in a
  rolled-back transaction and with an empty DB |
  files: `apps/services/models.py`, `apps/services/migrations/`,
  `apps/services/admin.py`, `templates/components/_testimonial_card.html`,
  `static/js/pixoria.js`, `static/admin/js/testimonial_kind.js` |
  commit: "feat(testimonials): real video and audio players"
- [ ] T52 — Mega-menu redesign (`templates/partials/_header.html` + CSS): a
  completely new design in the site's space/glass language — NO per-service
  descriptions. A wide glass panel with a row/grid of service tiles, each tile =
  a Lucide icon inside a small glowing planet-orb (accent color per service) +
  title only, hover animating an orbit ring around the orb; a slim bottom bar
  with the existing `mega_title` / `mega_cta_text` banner (D12, skipped when
  empty). The «خدمات» nav item MUST show a down-pointing chevron
  (`{% icon "chevron-down" %}`) that rotates when the menu is
  open/hovered/focused. Accessibility: `aria-haspopup`, `aria-expanded`,
  `aria-controls`, open on hover with a small close delay AND on click/Enter/
  Space, Esc closes, focus-visible styles, works on touch. Mobile overlay:
  services nested under the same item as an accordion with the chevron. Remove
  now-unused markup/CSS/context fields only if nothing else uses them |
  files: `templates/partials/_header.html`, `static/src/input.css`,
  `static/js/pixoria.js` | commit: "feat(header): redesign mega menu with orb tiles"
- [ ] T53 — INITIAL preloader (first visit only): space-themed (small orbiting
  planet + brand mark + thin gold progress ring/line), pure CSS, rendered by
  `base.html` before the content, shown once per browser session — a
  `sessionStorage` flag set by a tiny inline script in `<head>` that adds a
  `has-preloader` class to `<html>` (no flag → no overlay → no flash). Hard
  Lighthouse rules: no images/fonts/JS libraries needed; visible for at most
  ~800 ms; must remove itself via a CSS-only fallback animation (opacity → 0,
  `visibility: hidden`, `pointer-events: none` after ≤1.2 s) even if JS fails,
  with JS removing the node on `load` earlier when ready; must NOT block or
  delay LCP (not the LCP element itself — no large text/images), must not cause
  layout shift; `prefers-reduced-motion` → no preloader at all; honor
  `<noscript>`. Hero entrance animations start after the preloader hides |
  files: `templates/base.html`, `static/src/input.css`, `static/js/pixoria.js` |
  commit: "feat(base): first visit space preloader"
- [ ] T54 — Page-TRANSITION loader (lightweight, non-annoying): a thin gold
  gradient progress bar at the top plus, ONLY when a navigation takes longer
  than ~400 ms, a small orbiting-planet indicator in a corner — never a
  full-screen overlay, never blocking clicks. Nothing at all appears for fast
  navigations (start after a ~150 ms delay timer). Trigger on htmx requests
  that navigate (`htmx:beforeRequest` with `hx-boosted`/history push; ignore
  form-post requests except to disable the button) and normal same-origin link
  clicks (skip `target=_blank`, modifier keys, hash-only links, downloads,
  `mailto:`/`tel:`). Complete/hide on `htmx:afterSettle`, `pageshow` (bfcache
  restore) and `pagehide`, with a failsafe ~10 s timeout and
  `htmx:responseError`/`sendError` handling. Respect reduced motion (static bar,
  no spin). FIRST inspect how navigation currently works (D15 says hx-boost was
  dropped — confirm) and record the finding |
  files: `static/js/pixoria.js`, `static/src/input.css` |
  commit: "feat(base): page transition progress bar"
- [ ] T55 — Icon picker with live preview in admin: every Lucide icon field
  (all models using `validate_icon_name`, including `SocialLink`, Service,
  WhyFeature, ProcessStep, StatItem, TechSkill, AboutStat, ProjectStat,
  ContactFormPoint, …) gets a reusable admin widget `IconPickerWidget` (in
  `apps/core/icon_utils.py`): text input + live preview of the chosen icon + a
  searchable popup grid of available icons (search by name), keyboard
  accessible, no CDN, tiny vanilla JS in `static/admin/js/icon_picker.js`.
  Architecture: build a FULL Lucide sprite for ADMIN ONLY
  (`static/icons/lucide.full.sprite.svg`, loaded only on admin pages, never on
  the public site — add `lucide-static` as a devDependency if the package is not
  in `node_modules`), while the public sprite stays small. Add a management
  command `python manage.py sync_icons` that scans all icon fields in the DB +
  `{% icon "…" %}` usages in templates and rebuilds the public sprite via
  `scripts/build_icon_sprite.js` (idempotent). The widget must show a clear
  Persian warning when a chosen icon is not yet in the public sprite («این
  آیکون هنوز در اسپریت سایت نیست؛ دستور sync_icons را اجرا کنید») and
  `{% icon %}` must FAIL SOFT (render nothing, no exception) for unknown names.
  Keep `IconPreviewMixin` list previews working and document the workflow in
  this file | files: `apps/core/icon_utils.py`,
  `apps/core/templatetags/icon_tags.py`, `static/admin/js/icon_picker.js`,
  `apps/core/management/commands/sync_icons.py`, `scripts/build_icon_sprite.js` |
  commit: "feat(admin): icon picker widget and sync_icons command"
- [ ] T56 — Remove letter-as-logo placeholders: in Persian it is not customary
  to turn a name's first letter into a logo, and the «پ» tile looks bad. Grep
  all templates/CSS/JS for such placeholders (the about story fallback tile «پ»,
  header/footer brand mark, avatar initials in testimonials/team/author,
  `ClientMarqueeItem.mark` plates if they render a single letter, any
  `|first` / initial fallbacks) and replace them: brand mark fallback = the T57
  planet emblem SVG when no logo is uploaded; person avatars fallback = a
  neutral Lucide `user-round` icon in a gold-ringed orb; client plates show the
  full brand name (or admin-supplied short text); the story image fallback = a
  decorative orbit/planet illustration. List every replaced spot in this file |
  files: `templates/core/about.html`, `templates/partials/_header.html`,
  `templates/partials/_footer.html`,
  `templates/components/_testimonial_card.html`, `templates/blog/detail.html`, …
  | commit: "feat(brand): replace letter placeholders with emblems"
- [ ] T57 — LOGO + FAVICON option set: create 5–6 distinct SPACE /
  SOLAR-SYSTEM-themed logo concepts for «پیکسوریا / Pixoria» in `static/brand/`
  (e.g. `static/brand/option-1-orbit/`, `option-2-eclipse/`,
  `option-3-comet/`, …), each with `logo-full.svg` (mark + Persian wordmark),
  `logo-mark.svg`, `logo-mono-light.svg`, `logo-mono-dark.svg`, `favicon.svg`,
  `favicon-32.png`, `favicon-16.png`, `apple-touch-icon.png` (180),
  `icon-192.png`, `icon-512.png`, plus a `static/brand/README.md` and an
  `index.html` preview sheet (local only) showing all options side by side on
  dark and light backgrounds. Use the site palette (gold `#c9a15a` / `#e8c47a`
  / `#8f6b2c`, ink `#0a0a0c`, cream `#f5f3ee`, royal `#2e63ff`). Wordmarks must
  be converted to SVG PATHS (no font dependency): generate with a dev script
  `scripts/build_brand.js` (opentype.js + the local Vazirmatn / Space Grotesk
  files, `sharp` for PNG export — devDependencies, never runtime). Keep every
  SVG small and clean (optimized, `viewBox`, no embedded rasters); the marks
  must read well at 16–32 px (simple silhouettes) |
  files: `static/brand/**`, `scripts/build_brand.js` |
  commit: "feat(brand): space logo concept set"
- [ ] T58 — Brand selection wiring: add to `SiteSettings` a `logo_choice` and a
  `favicon_choice` (choices auto-discovered from the folders in
  `static/brand/`, shown in the admin with a small image preview next to each
  option and Persian help_text) while keeping the existing uploaded `logo` /
  `favicon` / `apple_touch_icon` fields as OVERRIDES — an uploaded file wins
  over a chosen preset. Wire a context-processor helper (a `brand` dict with
  resolved URLs) into `base.html` (`<link rel="icon">` svg + png fallbacks,
  apple-touch-icon, `site.webmanifest` icons, `theme-color`), the header, the
  footer, the JSON-LD logo and the OG image fallback. Default choice = option 1
  so nothing breaks on an empty DB. Never overwrite existing uploads. Migration
  + admin + a `collectstatic --dry-run` check |
  files: `apps/core/models.py`, `apps/core/migrations/`, `apps/core/admin.py`,
  `apps/core/context_processors.py`, `templates/base.html`,
  `templates/partials/_header.html`, `templates/partials/_footer.html` |
  commit: "feat(core): brand choice wiring in site settings"
- [ ] T59 — About hero visual → animated SOLAR SYSTEM: replace the CSS "orbit
  pills" artwork on the left of the about hero with a real solar-system
  composition — a glowing gold sun/star in the centre, concentric elliptical
  orbit rings, and one planet per `Service` (from the DB, max ~6; each planet
  gets its own size/speed/accent color and shows the service icon, with the
  service TITLE as a label chip next to it, readable and counter-rotated so it
  never turns upside down), plus a few tiny moons/asteroid dots. Pure CSS/SVG
  animation (transform rotate with different durations, counter-rotation for
  labels), GPU-friendly, paused when off-screen (IntersectionObserver toggling
  `animation-play-state`), static under `prefers-reduced-motion`, degrading
  gracefully with 1–6 services; hover/focus on a planet highlights its orbit
  and links to the service page; responsive (scales down on mobile without
  overflow) | files: `templates/core/about.html`, `static/src/input.css`,
  `static/js/pixoria.js` | commit: "feat(about): animated solar system hero visual"
- [ ] T60 — Space identity pass (light touch, performance-safe): define a tiny
  set of reusable decorative utilities in `input.css` (`.orbit-ring`,
  `.orbit-dot`, `.planet-orb` with accent variants, `.star-field` as a CSS-only
  subtle starfield for dark sections) and apply them sparingly to existing dark
  section backgrounds and inner-page heroes (portfolio/blog/contact/about) so
  the whole site feels like one "solar system" — no images, no heavy JS, no new
  3D. Record the utilities and where they are used |
  files: `static/src/input.css`, inner-page heroes | commit: "feat(css): space identity utilities"

### Phase 12 — Dedicated SERVICE pages (design from `new/services/*.html`)

Design inputs: `new/services/{web-design,programming,graphic-design,logo-design}.html`
(study their structure, copy and per-service atmosphere), the whole converted
site (`static/src/input.css`, the home partials, the components, the
header/footer/CTA) and the existing models `services.Service`, `ServiceStat`,
`ServiceWhyUs`, `ServiceDeliverable`, `ServiceProcess`, `ServicePlan`,
`ServiceCustomItem`, `ServiceFAQ`, `ServiceTestimonial`. Services already have
`icon`, `visual` (none/browser/terminal/palette/diamond), `chips` and `badge`.

- [ ] T61 — Review and extend the service models (reuse first; add only what is
  missing; everything optional): a per-service theme/accent (`accent` color
  choice mapped to CSS classes; the hero `visual` kept), hero fields (eyebrow,
  h1 with `[[ ]]`, lead paragraph, two CTA labels/URLs), long-form SEO content
  blocks as a new ordered child model `ServiceSection` (eyebrow, `[[ ]]` title,
  rich-text body, optional image + alt, `layout` left/right/full, order,
  is_active) so the admin can add as many sections as needed, `ServiceTool`
  (name, optional icon, order) for tools/technologies, `ServiceUseCase` /
  industries (title, icon, short text), a related-services selection (M2M to
  self, optional), a REAL `Portfolio.service` relation (nullable FK or M2M to
  `Service`) with a data migration that best-effort maps the existing free-text
  `service_type` to services by title (NEVER delete `service_type`), and an
  optional `Article.related_services` M2M; SEO fields (`meta_title`,
  `meta_description`, optional `og_image`). Update `projects_carousel(service=…)`
  / `articles_carousel` / `testimonials_slider(service=…)` to use the real
  relations, keeping the text fallback. PRICING: exactly 3 plans per service
  managed by `ServicePlan` (name, short tagline, optional integer `price` +
  `price_prefix` like «از» + currency label defaulting to «تومان» + optional
  `price_note` / custom text like «تماس بگیرید» when the price is empty,
  ordered `features` child with an `is_included` flag so the admin can show
  crossed-out items, `is_featured` "most popular", CTA label/url, order,
  is_active); admin inline `max_num=3`, `extra=3`, validation that at most one
  plan is featured. Add the `fa_price` filter (thousands separators + Persian
  digits). Migrations + admin (fieldsets, inlines, `list_editable`, previews),
  no data loss | files: `apps/services/models.py`, `apps/services/migrations/`,
  `apps/services/admin.py`, `apps/portfolio/models.py`, `apps/blog/models.py`,
  `apps/core/templatetags/fa_digits.py` |
  commit: "feat(services): extend models for dedicated pages"
- [ ] T62 — Seed command `seed_services_content.py` (idempotent; never
  overwrite admin edits; the D21/D25 collection-cleanup pattern only for rows
  it created): verbatim/adapted Persian copy from the four `new/services/*.html`
  pages PLUS newly written, high-quality, UNIQUE Persian copy per service for
  the extra sections (see the content plan below). Write natural SEO copy: one
  clear topic per section, semantic headings, no keyword stuffing, no
  duplicated paragraphs between services, realistic Iranian market context
  (Mashhad/Iran, response times, Persian/RTL specifics). Seed three plausible
  plans per service with placeholder prices the admin will change |
  files: `apps/services/management/commands/seed_services_content.py` |
  commit: "feat(services): seed per-service content"
- [ ] T63 — `templates/services/detail.html` skeleton on `base.html` (the D27
  language): per-service theme classes, the breadcrumb partial (T47), JSON-LD
  placeholders in `extra_head`, a hero by `visual` type (bespoke artwork,
  CSS/SVG only) and the intro/overview section. Every section `{% if %}`-guarded;
  the page must render with an empty DB for that service's children |
  files: `templates/services/detail.html`, `apps/services/views.py` |
  commit: "feat(services): v2 detail page skeleton"
- [ ] T64 — Content sections part 1: «چه کاری انجام می‌دهیم»
  (features/deliverables), the long-form `ServiceSection` blocks (alternating
  layout, `.prose-ink` / `.prose-cream`), use-cases/industries, and the tools &
  technologies marquee/chips | files: `templates/services/detail.html` |
  commit: "feat(services): detail content sections one"
- [ ] T65 — Content sections part 2: the process timeline (`ServiceProcess`),
  why-us (`ServiceWhyUs`), the stats counters (`ServiceStat`) and the
  delivery/timeline note | files: `templates/services/detail.html`,
  `static/js/pixoria.js` | commit: "feat(services): detail content sections two"
- [ ] T66 — PRICING section: three plan cards (the featured one elevated with a
  gold border + a «محبوب‌ترین» badge), a features list with included/excluded
  icons, the price formatted via `fa_price`, a CTA per plan (defaulting to
  `contact:contact` with `?plan=<slug>&service=<slug>` so the contact form can
  prefill the subject — implement the prefill in the contact view/form WITHOUT
  breaking T34 behavior) and the custom-request block from `ServiceCustomItem`.
  Responsive: 3 columns on desktop, stacked or a snap-carousel on mobile. The
  section is hidden when there are no active plans and renders 1–3 plans
  gracefully | files: `templates/services/detail.html`, `apps/contact/views.py`,
  `apps/contact/forms.py` | commit: "feat(services): pricing section with plan cta"
- [ ] T67 — Social proof + discovery sections: `{% testimonials_slider
  service=service %}`, `{% projects_carousel service=service %}` (related work),
  the FAQ accordion (`ServiceFAQ`, reusing `.faq-item` + `initFaq`),
  related-services cards, `{% articles_carousel %}` filtered by the service's
  related articles, and the final CTA from base. JSON-LD: `Service` (+ `provider`
  Organization, `areaServed`, `offers` as an `Offer` list built from the plans
  with `priceCurrency` IRR/IRT handled correctly), `FAQPage` and
  `BreadcrumbList` — all built with the `json` filter and skipping pieces with
  no data so the JSON never breaks | files: `templates/services/detail.html` |
  commit: "feat(services): social proof and discovery sections"
- [ ] T68 — Per-service atmosphere: web-design (browser mockup + layout-grid
  motifs), programming (terminal/code motifs), graphic-design (palette/swatch
  motifs), logo-design (diamond/geometry/construction-grid motifs). Implement
  these as `service-theme-*` class sets + the four hero artworks, all CSS/SVG
  (no images), reduced-motion safe, lazily animated, each tied to the service's
  planet/orb accent so it sits inside the site's "solar system" identity |
  files: `templates/services/detail.html`, `static/src/input.css` |
  commit: "feat(services): per-service hero atmospheres"
- [ ] T69 — Services LIST page `templates/services/list.html` redesign: hero,
  service cards using the same orb/planet language as the mega menu (T52), a
  "how we choose" section, FAQ if available, CTA from base; then a
  view/sitemap/internal-links check and a render of every service page + the
  list with an EMPTY database and with seeded data; `manage.py check`,
  `makemigrations --check`, `npm run build` |
  files: `templates/services/list.html`, `apps/services/views.py` |
  commit: "feat(services): redesign list page"

Content plan for each service page (adapt per service, never copy-paste between
services): hero (h1 + lead + CTAs + bespoke artwork) → overview («X چیست و چرا
مهم است») → what we deliver → long-form guide sections (3–5 blocks: process
specifics, technical/design choices, mistakes to avoid, how pricing is
determined, how long it takes) → use-cases/industries → tools & technologies →
process timeline → why us → stats → pricing (3 plans) + custom request →
portfolio carousel (this service) → testimonials slider (this service) → FAQ
(8–10 real questions) → related services → related articles → CTA/footer (base).
One `<h1>`; logical h2/h3; internal links between services, portfolio, blog and
contact; descriptive alt texts; meta title/description per service.

### Phase 13 — Cleanup (RUN LAST)

- [x] T41 — Verify no broken references (grep for removed
  classes/tags/includes), fix `templates/registration/login.html`,
  `templates/admin/login.html`, proposal page and any remaining page that
  still assumes the old base | commit: "fix(templates): align remaining pages with v2 base"
- [x] T42 — superseded by Phase 12 (service pages are fully redesigned) — the
  minimal placeholders this task produced (D46) are replaced by T63–T69.
- [ ] T43 — Delete ALL old frontend files (unreferenced static CSS/JS, old
  templates/partials/components, unused template tags/context
  processors/views/URLs created only for old templates). Before deleting, list
  candidates in this file and verify with a project-wide grep. One small commit
  per group | commit: "chore: remove obsolete v1 frontend assets"
  Status so far: the orphaned blog detail partials, `_manifesto.html` +
  `_works.html` and the whole v1 `templates/components/` + `components/cards/`
  tree were already deleted by commits `9d59609` and `ba9bb99`; the v1 static
  assets are deleted on disk and STAGED (23 files: `static/js/core/*`,
  `static/js/pixoria-bg/*`, `static/js/engine/*`, `static/js/{main,motion,cursor,
  home-motion,header-motion,footer-stars}.js`, `static/css/{blog,site,styles}.css`
  and `apps/core/templatetags/anim_tags.py`) — verified unreferenced, commit them
  as the first T43 group. Remaining candidates to check with a grep: anything
  else that only existed for the v1 templates (unused context processors, views,
  URLs, `HomeLead` leftovers if T45 leaves any, the v1 `ContactInfo` model that
  D35/D36 flagged as vestigial, `PackagesSection`/`Package`/`PackageFeature` and
  `HeroMarqueeItem` that D18/D19 kept but never render, `AboutMission`/
  `AboutValue`/`AboutPre`/`TeamMember`/`AboutProcessStep`/`AboutFaq` that D33
  left untouched — delete a model only with a migration and after confirming no
  admin/seed/template references it).
- [ ] T44 — Final checks: `python manage.py check`,
  `makemigrations --check --dry-run`, `collectstatic --dry-run`, render
  home/about/contact/404/portfolio/blog (list + detail) with an EMPTY database
  and with seeded data, Lighthouse-minded review; then delete `new/` as a
  separate final commit | commit: "chore: remove new/ prototype after migration"

## Current status

T01–T49 done (T42 superseded by Phase 12; T47b was the template-comment leak
sweep — D50). **Next: T50** — home portfolio responsive layout: 3-column grid
at `lg`, carousel (2/view) at `md`, carousel (1/view) on mobile — ONE DOM,
filter working in both modes.


