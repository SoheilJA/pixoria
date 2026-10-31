# AGENT_PROGRESS — Pixoria Redesign (Ryoku Design Language)

## 1. Project goal

Redesign the entire Pixoria corporate website (Django 5.2 templates + Tailwind CSS v4,
Persian/RTL) with the "Ryoku" reference design language: warm near-black background
(#0d0e0c), raised surfaces (#121311), a single sand/beige accent (#d8cfc0), 1px hairlines,
a serif display face for headings (Persian: Amiri), a grotesk for body (Vazirmatn) and a
tiny wide-tracked label face (Space Grotesk), square corners, filmstrip/halftone imagery,
minimal vanilla-JS animations. The goal is the same design FAMILY as the reference — not a
pixel copy. Content, models, views, URLs and texts stay untouched; only appearance and HTML
structure change. Work proceeds section by section on the homepage, then header/footer and
inner pages. Full reference spec: `prompt/prompt.md` (section 1).

## 2. Finalized design system

**Tailwind v4 tokens** — defined in `styles/input.css` `@theme` (this project has NO
`tailwind.config`; Tailwind v4 CSS-first config is the equivalent of theme.extend):

| Token | Value | Use |
| --- | --- | --- |
| `--color-void` | `#0d0e0c` | main page background (`bg-void`) |
| `--color-surface` | `#121311` | raised cards/panels (`bg-surface`) |
| `--color-sand` | `#d8cfc0` | the ONLY accent + primary text (`text-sand`, `border-sand`) |
| `--color-line` | `#d8cfc0` | hairlines, always with opacity modifier (`border-line/10`, `/14`) |
| `--font-display` | Amiri, Vazirmatn, serif | headings (NO negative letter-spacing for Persian) |
| `--font-body` / `--font-sans` | Vazirmatn | body text |
| `--font-label` / `--font-latin` | Space Grotesk | tiny labels, numbers, meta (uppercase + wide tracking, Latin only) |

**Custom CSS classes** — one block in `styles/input.css`, marked
`/* ---------- Ryoku design system (بازطراحی) ---------- */`:

- `.ry-label` — tiny label: Space Grotesk, 9–11px, uppercase, tracking 0.18–0.25em, sand/50.
- `.ry-btn` + `.ry-btn--fill` (sand bg, dark text) / `.ry-btn--line` (hairline border only).
  Square (rounded-none), hover inverts colors, 180ms transition.
- `.ry-frame` — image frame: 1px hairline border + 4 corner marks (+ shapes, CSS-only via
  background gradients on ::before/::after).
- `.ry-halftone` — monochrome halftone image treatment: grayscale + contrast filter on img,
  dot-pattern overlay (repeating radial-gradient ~4px) tinted sand via mix-blend-mode.
- `.ry-reveal` / `.ry-reveal.is-in` — scroll reveal: opacity 0 → 1, translateY(16px) → 0,
  700ms ease; driven by `static/js/ry-reveal.js` (vanilla IntersectionObserver, honors
  `prefers-reduced-motion`, `data-delay` for stagger).
- `.ry-sec-head` — section header pattern: mono number+title row, hairline stretching to
  the end, small glyph at the end (Persian single letters, see glyphs below).
- `.ry-ghost` — huge outline-only text (webkit-text-stroke, ~8% opacity) for footer.
- `.ry-stat` — square stat box: hairline border, large display number, tiny label below.
- `.ry-row` — compact list row: hairline separators, small icon + title + mono subtitle + number.
- `.ry-inv` — inverted block: sand background, dark text (only for the most important CTAs).

**Scope override**: inside `.ry-serif` elements, the old `text-goldgrad` spans (from the
`[[کلمه]]` admin syntax, produced by the `highlight` filter) are overridden to solid sand
+ weight 500 — old gradient is neutralized without touching backend.

**Partials** (`templates/components/`):
- `_ry_section_header.html` — props via `with`: `ry_num` ("02"), `ry_label` ("درباره ما"
  or short Latin tag), `ry_glyph` (one glyph), optional `ry_title`, `ry_text`.
- `_ry_frame.html` — image inside `.ry-frame` with halftone + corner marks; props:
  `ry_src`, `ry_alt`, `ry_caption` (e.g. "01 / 04 · عنوان"), optional `ry_bg` circle ornament.

**Fonts** (self-hosted, no CDN): `static/fonts/amiri-{400,700}-{arabic,latin}.woff2`
added to `static/fonts/font_urls.css` (display serif). Vazirmatn (body) and Space Grotesk
(labels/mono) already existed.

**Glyph convention** (kanji from the reference replaced by single Persian letters, one per
section, consistent site-wide, rendered in font-display): about «هـ» (هویت) · services «خـ»
(خدمت) · portfolio «پـ» (پروژه) · why «چـ» (چرا) · process «فـ» (فرآیند) · tech «تـ»
(تکنولوژی) · testimonials «نـ» (نظر) · stats «آ» (آمار) · blog «مـ» (مقاله) · faq «سـ»
(سؤال) · hero «ا» (آغاز).

**Build pipeline**: Tailwind v4 CLI. `npm run build` compiles `styles/input.css` →
`static/css/tailwind.css`. WhiteNoise serves from `public/static`, so after ANY static
change: `venv\Scripts\python manage.py collectstatic --noinput`. Verify pages with
`venv\Scripts\python scripts\render_check.py`.

## 2b. Image policy (USER INSTRUCTION — DO NOT FORGET)

This is a direct user instruction for the WHOLE redesign; every future section must obey it:

1. **Real uploaded images stay real (never replace, never restyle into ASCII):**
   - **Portfolio images** — uploaded in the admin panel; shown EXACTLY as uploaded in the
     portfolio carousel (home + archive) and the single portfolio detail page.
   - **Blog cover images** — uploaded in the admin panel; shown EXACTLY as uploaded in the
     blog carousel, the all-articles page and the single article page.
   These two image sets keep their uploaded appearance (the Ryoku halftone treatment used
   in home sections is a CSS overlay — the files themselves are untouched).
2. **Everywhere else** (all decorative/illustrative imagery on the site): replace with
   **ASCII art** — real ASCII DRAWINGS rendered as imagery (monospace, block-art), NOT
   simply large text. Prefer an animated/video-like variant (ASCII animation) if feasible.
3. **For now: do NOT create the ASCII art yet.** Whenever the redesign reaches a spot that
   needs imagery, put a clearly marked PLACEHOLDER (Ryoku hairline frame + tiny label,
   e.g. `ASCII-ART-PLACEHOLDER`) so it is easy to find later. After the ENTIRE site is
   redesigned, we will come back and produce all the ASCII art in one pass.
4. Tracker: when a placeholder is introduced, list its location in section 4's notes so the
   final ASCII pass finds them all (grep hint: `ASCII-ART-PLACEHOLDER`).

## 3. Fixed rules

- Tailwind utilities only; a small custom-CSS block in `styles/input.css` for noise,
  halftone, @font-face, keyframes. No new JS/CSS libraries (vanilla JS only).
- Do NOT touch backend: views, models, urls, context, variable names. Django template tags
  and dynamic data keep working. Keep current texts (shorten only if design demands, same
  meaning).
- RTL: logical properties (ms-/me-/ps-/pe-/start-/end-). Persian headings never get negative
  letter-spacing; uppercase/tracking for Latin only; "italic" emphasis = weight/color change
  (never synthetic slant).
- Responsive 360px → wide; multi-column collapses to single with hairlines kept.
- Accessibility: readable contrast, semantic HTML, sand focus ring, aria on accordion/slider.
- Repeated elements become partials/components (DRY).
- ONE Persian one-line commit per section/stage, progress file included in the same commit,
  explicit `git add` of related files only, never push, never commit broken work.

## 4. Section checklist (homepage, top → bottom; order from DB `HomeSection`)

| # | Section | Template | Status | Commit |
| --- | --- | --- | --- | --- |
| — | Foundation (tokens, fonts, base components) | `styles/input.css` + `static/fonts/` + partials + `ry-reveal.js` | ✅ | «راه‌اندازی توکن‌ها و کامپوننت‌های پایه‌ی طراحی جدید» |
| — | Header/navigation | `templates/partials/_header.html` | ⬜ (last) | — |
| 1 | Hero | `templates/home/sections/_hero.html` | ⬜ (last) | — |
| 2 | درباره ما (about) | `templates/home/sections/_about.html` | ⏸ waiting for user approval | «بازطراحی سکشن دوم (درباره ما) با زبان طراحی جدید» |
| 3 | خدمات (services) | `templates/home/sections/_services.html` | ✅ | «بازطراحی سکشن سوم (خدمات)» |
| 4 | نمونه‌کارها (portfolio) | `templates/home/sections/_portfolio.html` | ✅ | «بازطراحی سکشن چهارم (نمونه‌کارها)» |
| 5 | چرا پیکسوریا (why) | `templates/home/sections/_why.html` | ✅ | «بازطراحی سکشن پنجم (چرا پیکسوریا)» |
| 6 | فرآیند کار (process) | `templates/home/sections/_process.html` | ✅ | «بازطراحی سکشن ششم (فرآیند کار)» |
| 7 | تکنولوژی‌ها (tech) | `templates/home/sections/_tech.html` | ✅ | «بازطراحی سکشن هفتم (تکنولوژی‌ها)» |
| 8 | نظرات مشتریان (testimonials) | `templates/components/testimonials_slider.html` + `_testimonial_card.html` | ✅ | «بازطراحی سکشن هشتم (نظرات مشتریان)» |
| 9 | آمار و ارقام (stats) | `templates/home/sections/_stats.html` | ✅ | «بازطراحی سکشن نهم (آمار و ارقام)» |
| 10 | آخرین مقالات (blog) | `templates/home/sections/_blog.html` + `#blog`-scoped CSS | ✅ | «بازطراحی سکشن دهم (آخرین مقالات)» |
| 11 | سوالات متداول (faq) | `templates/home/sections/_faq.html` + `.ry-faq-sec`-scoped CSS | ✅ | «بازطراحی سکشن یازدهم (سوالات متداول)» |
| 12 | CTA (همهٔ صفحات) | `templates/partials/_cta.html` | ✅ | «بازطراحی سکشن CTA (همهٔ صفحات)» |
| 13 | Footer + ghost text | `templates/partials/_footer.html` | ✅ | «بازطراحی فوتر» |
| — | Global review + inner pages (about/contact/blog/portfolio/services detail, 404, login) | — | ⬜ | — |

## 5. Exact current state

- Stage A (foundation) DONE and committed (`b2e4a93`).
- Stage B (section 2 — about) DONE, committed (`8f18548`) and approved by the user.
- Section 3 (services) DONE, verified in the browser (desktop + 360px, zero console
  errors) and committed.
- Section 4 (portfolio) DONE, verified in the browser (filter hide/show + count + empty
  message + mobile snap track + dots + zero console errors) and committed. New shared
  partial `components/_ry_project_card.html` (Ryoku project card) keeps ALL interaction
  hooks of pixoria.js: `pf-item` + `data-cat` + `is-hidden`/`pf-in`/`is-in` for the filter
  and child-of-`data-carousel-track` for the mobile carousel; old classes (`flt-btn`,
  `ctrl-btn`, `slider-dot`) are restyled via `.ry-scope`-scoped CSS overrides so the
  archive page (old design) is unaffected. Mobile track keeps `gap-6` = GAP(24px) of the
  carousel JS; desktop uses the 1px hairline grid.
- Section 5 (why) DONE, verified (desktop + 360px, zero console errors) and committed.
  Compact list-row layout (number + icon + serif title + description, hairline rows).
  The old per-feature SVG illustrations were REMOVED — this section has no imagery in the
  new language, so per the image policy (§2b) no ASCII placeholder is needed here.
  NOTE: `.ry-row` no longer force-centers its items (`align-items` removed from the class
  on purpose — rows set their own alignment); `column-gap: 1rem` kept.
- Section 6 (process) DONE, verified (desktop + 360px, zero console errors) and committed.
  Vertical step list connected by a 1px hairline (`.ry-process`), square node with the
  step icon on the rail, mono numbers, serif titles. The old glowing-bead rail animation
  was removed (new language = static hairline + simple reveal).
- Section 7 (tech) DONE, verified (desktop + 360px, zero console errors) and committed.
  "Spec sheet" hairline grid (2/3/4 cols responsive) — each cell: small icon + Latin name
  in Space Grotesk with tracking. The old orbit/CSS-art illustration removed (no imagery
  in the new language → no ASCII placeholder needed per §2b).
- Section 8 (testimonials) DONE, verified (slider next/prev + dots, desktop + 360px, zero
  console errors) and committed. The shared inclusion-tag component (`testimonials_slider`
  queries `ServiceTestimonial` itself — the home view provides no items) serves BOTH home
  and service-detail pages, and the Python tag could not be touched (backend rule), so the
  template got a THEME BRANCH on `section_id`: `id="testimonials"` (home default) renders
  the Ryoku version (ry-scope section, ry-sec-head «08» + glyph «نـ», serif heading,
  `.ry-tcard` cards, square ctrl-btn/dots via existing `.ry-scope` overrides); any other id
  (service detail) keeps the old design untouched. Same branch in `_testimonial_card.html`
  (`ry=1` flag). `t-card` hook class + `t-cols-3` track + `data-slider*` contract kept so
  pixoria.js works unchanged. Reveal sits on the TRACK (not per card) — per-card IO reveal
  would leave off-screen horizontal cards invisible.
- Section 9 (stats) DONE, verified (Persian-digit counters ۱۵/۵۰۰+/۹۸٪/۲۴/۷ animate on
  view, desktop + 360px, zero console errors) and committed. Reuses `.ry-stat-grid`/
  `.ry-stat` from the about section; the counter hook here is `data-count` (+ prefix/
  suffix) — DIFFERENT from about's `data-counter` — both pixoria.js systems kept intact.
  Old light cream background, glass cards and the stroke "PIXORIA" text removed.
- POLICY FIX (per §2b clarification): REAL content images must display EXACTLY as uploaded
  → the halftone/grayscale treatment was REMOVED from `_ry_project_card.html` (section 4
  cards), the about filmstrip main image + thumbnails (natural color now, hover = subtle
  scale), and `.ry-thumb img`/`.ry-pcard` CSS filter rules deleted. `.ry-halftone` class
  stays in CSS (unused, reserved for decorative ASCII-era imagery only).
- Section 10 (blog) DONE, verified (10 cards, square hairline cards, Amiri titles, old
  gold gradient overlay hidden, carousel next/dots working, mobile 360 no overflow, zero
  console errors) and committed. The articles carousel is SHARED (home + service detail +
  blog detail) and its inclusion tag passes no distinguishing context, so it could NOT get
  a template branch; instead the home section wraps `{% articles_carousel %}` inside
  `#blog` (ry-scope) and the whole look is transformed via `#blog`-scoped CSS overrides
  (higher specificity; inline `border-radius:1.75rem` neutralized with scoped
  `!important`). Covers render as uploaded (no filter). `data-carousel*` + `ctrl-btn` +
  `slider-dot` hooks untouched.
- Section 11 (faq) DONE, verified (accordion opens/exclusive-close/aria, desktop + 360px,
  zero console errors, contact-page regression clean) and committed. FAQ accordion classes
  are SHARED (home + services list + service detail + contact), and `id="faq"` is
  DUPLICATED on the contact page — so `#faq` scoping LEAKED there at first attempt; the
  scope is the unique home-only class `.ry-faq-sec` on the section instead. Hooks
  (`.faq-item`/`.faq-q`/`.faq-a` + `.open` + maxHeight) untouched.
- LESSON (tooling): NEVER edit files via PowerShell `Get-Content`/`Set-Content` — PS 5.1
  reads UTF-8-no-BOM as ANSI and re-encoding mangles ALL Persian comments in the file
  (happened once; recovered via `git checkout HEAD -- styles/input.css` + re-adding the
  block through the edit tool). Use the dedicated edit/write tools for ANY text change.
- Section 12 (CTA) DONE, verified (inverted sand block + dark serif title + void terminal
  panel + dark buttons, desktop + 360px, zero console errors) and committed. This partial
  is included ONCE in base.html (all pages) — fully rewritten with the Ryoku "inverted
  block" rule (sand bg, dark text — the site's most important CTA). The terminal ASCII
  texts kept verbatim, restyled as `.ry-term` (void panel, mono Space Grotesk, square
  status dots).   New dark button variants `.ry-btn--ink`/`.ry-btn--ink-line`; `.ry-inv`
  highlight override added. Old space motifs (shards, orbit layer, aurora) removed.
  Old `terminal-terminal__*` classes now unused (cleanup at global review).
- Footer DONE (user redirected: footer before hero), verified (void bg, no canvas,
  hairline contact rows, spec-sheet trust boxes, 302px outline ghost «پیکسوریا» cropped
  exactly at the page end, desktop + 360px, zero console errors) and committed. The live
  field canvas (hx-field/hero-field.js) was removed from the footer; hero-field.js stays
  for the hero until its redesign. Shared `_brand_lockup.html` (official logo) untouched.
  New `.ry-soc` square social buttons. User-requested addition (commit
  «افزودن ستون صفحات اصلی به فوتر»): a static main-pages nav column («صفحات اصلی»: خانه /
  درباره ما / تماس با ما / مجله via `{% url %}`) between the brand and services columns;
  column spans rebalanced 4+2+3+3. Note: the about URL name is `core:about` (NOT `about`).
- Environment notes: this local DB had no readable work images, so `about_works` rendered
  the fallback panel; a placeholder `public/media/portfolio/images.jpg` (gitignored) was
  created to test the filmstrip path — `public/media` is not committed. The filmstrip
  branch with 4 works was also verified by direct template rendering.
- Gotcha learned: the dev server was started with `--noreload`, and Django 4.1+ caches
  templates per process even in DEBUG — after editing a template, RESTART the server or
  drop the `--noreload` flag, otherwise stale markup is served (cost some debugging time).

## 6. Decisions and important notes

- Reference screenshots exist in `prompt/` but the agent cannot view images (model
  limitation); the design system was implemented from the detailed written spec in
  `prompt/prompt.md` §1.
- Project uses Tailwind v4 CSS-first config → tokens go in `@theme` in `styles/input.css`
  (equivalent of tailwind.config theme.extend).
- New tokens use NEW names (`void`, `surface`, `sand`, `line`) instead of redefining the old
  `ink/gold/cream` tokens, so old not-yet-migrated sections keep rendering during the staged
  migration; old tokens get consolidated at the global review stage.
- `.grain` noise layer already existed in `base.html` (feTurbulence SVG, fixed,
  pointer-events-none) — its opacity was tuned to ~4.5% (was 6%), inside the 3–5% spec.
- Kanji section glyphs replaced by single Persian letters (see glyph table above).
- Persian display font: Amiri (self-hosted woff2 via jsDelivr fontsource download, OFL) —
  closest free Persian serif with character; italic emphasis in Persian = color/weight
  change only.
- Old reveal system (`data-reveal` + motion.css + pixoria.js) untouched; new sections use
  the separate lightweight `.ry-reveal` + `ry-reveal.js` so the two systems never fight.
- `[[کلمه]]` highlight spans (gold gradient) are visually overridden to solid sand inside
  Ryoku sections via scoped CSS — backend filter untouched.
- About stats keep the existing `data-counter` mechanism from pixoria.js (Persian digits)
  inside the new square stat boxes.
- About section image panel replaced by a Ryoku filmstrip: 1 large framed halftone image +
  4 thumbnails + "1 / 4" counter + square arrows, driven by tiny vanilla JS in
  `static/js/ry.js` (`data-ry-filmstrip` scope).

## 7. Next step

Remaining: section 1 (hero, `templates/home/sections/_hero.html` — the last old-design
part of the homepage; its hero-field canvas must become a Ryoku-appropriate visual or an
ASCII-ART-PLACEHOLDER per §2b), then the header (`templates/partials/_header.html`), then
the global review + inner pages (about/contact/blog/portfolio/services lists + details,
404, login). One commit per step, update this file before each commit. ASCII-art pass
(all `ASCII-ART-PLACEHOLDER` spots) happens AFTER the full redesign.

## 8. Resume instruction

Read this file fully, run `git status` (tree must be clean; if not, report first), check
section 7 for the next action and section 4 for the exact status of every section, then
continue from "Next step". After each section: `npm run build`,
`venv\Scripts\python manage.py collectstatic --noinput`, verify with
`venv\Scripts\python scripts\render_check.py`, update this file, make ONE Persian commit.
