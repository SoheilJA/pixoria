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
| 2 | درباره ما (about) | `templates/home/sections/_about.html` | ⬜ | — |
| 3 | خدمات (services) | `templates/home/sections/_services.html` | ⬜ | — |
| 4 | نمونه‌کارها (portfolio) | `templates/home/sections/_portfolio.html` | ⬜ | — |
| 5 | چرا پیکسوریا (why) | `templates/home/sections/_why.html` | ⬜ | — |
| 6 | فرآیند کار (process) | `templates/home/sections/_process.html` | ⬜ | — |
| 7 | تکنولوژی‌ها (tech) | `templates/home/sections/_tech.html` | ⬜ | — |
| 8 | نظرات مشتریان (testimonials) | `templates/home/sections/_testimonials.html` | ⬜ | — |
| 9 | آمار و ارقام (stats) | `templates/home/sections/_stats.html` | ⬜ | — |
| 10 | آخرین مقالات (blog) | `templates/home/sections/_blog.html` | ⬜ | — |
| 11 | سوالات متداول (faq) | `templates/home/sections/_faq.html` | ⬜ | — |
| 12 | CTA (همهٔ صفحات) | `templates/partials/_cta.html` | ⬜ | — |
| 13 | Footer + ghost text | `templates/partials/_footer.html` | ⬜ (last) | — |
| — | Global review + inner pages (about/contact/blog/portfolio/services detail, 404, login) | — | ⬜ | — |

## 5. Exact current state

- Stage A (foundation) is DONE and committed (see checklist). Verified: `npm run build` OK,
  `collectstatic` OK, `render_check.py` all pages 200 / clean. Note: `node_modules` was
  missing and `npm install` was run as part of setup.
- Stage B (section 2 — about) has NOT started. Git tree clean after the Stage A commit.

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

Stage B: redesign ONLY section 2 of the homepage — the "about" section
(`templates/home/sections/_about.html`, second section after the hero) — with the Ryoku
system (section header «02 · درباره» + glyph «هـ», serif display heading, narrow text
column, filmstrip slider for `about_works`, square stat boxes for `about_stats`). Do not
touch the hero/header/other sections. Then: build + collectstatic + verify, update this
file, commit «بازطراحی سکشن دوم (درباره ما) با زبان طراحی جدید», and STOP for user
approval.

## 8. Resume instruction

Read this file fully, run `git status` (tree must be clean; if not, report first), check
section 7 for the next action and section 4 for the exact status of every section, then
continue from "Next step". After each section: `npm run build`,
`venv\Scripts\python manage.py collectstatic --noinput`, verify with
`venv\Scripts\python scripts\render_check.py`, update this file, make ONE Persian commit.
