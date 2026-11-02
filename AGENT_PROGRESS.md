# AGENT PROGRESS — Pixoria UI/UX + ASCII overhaul
Source of truth: this file. If you (the agent) were interrupted: read this file fully, find the first unchecked [ ] item, check "Last action" + `git status`/`git diff` to see if it was half-done, finish it, and continue. Never redo [x] items.

## RESUME PROTOCOL
1. Read this file. 2. Read "DECISIONS" (tokens, file paths). 3. Continue at first [ ] item. 4. After each sub-step: tick it, update "Last action". 5. Chat replies to the user in Persian; everything else English.

## DECISIONS (fill in as discovered)
- Base template: templates/base.html   - CSS entry: styles/input.css (Tailwind v4) + static/css/ry.css (custom)   - JS entry: static/js/pixoria.js + static/js/ry.js + static/js/ry-reveal.js + static/js/hero-field.js
- Login template: templates/registration/login.html   - Contact template: templates/contact/contact.html
- Cream token: --color-sand (#d8cfc0) / --cream (#f5f3ee)   - Dark bg token: --color-void (#0d0e0c) / --ink (#0a0a0c)   - Accent token: --accent: #D97757 (new, to add)
- ASCII files: static/js/ascii/engine.js, static/js/ascii/scenes/*.js, static/css/ascii.css, templates/components/ascii.html (to create)

## LAST ACTION
(2026-11-02) P9 complete — All ASCII-ART-PLACEHOLDER occurrences replaced with custom engine.js + scenes/*.js:
- About page: hero panel (armada-horizon), story panel (deep-space-drift)
- Contact page: map section (globe)
- Service detail: hero panel (globe), section panels (deep-space-drift)
- Home hero: armada-horizon
- Home services: globe/starship/ringed-planet/galaxy-fleet
- Pre-footer band: deep-space-drift
Fixed cliff-lighthouse-night 404 by switching to armada-horizon. Fixed TemplateSyntaxError in services/detail.html by adding {% load static %}.

## BLOCKERS / ASSUMPTIONS
- (none yet)

## AUDIT (problems found + chosen fix)
1. **Gradients everywhere** — ~100+ gradient usages in input.css/ry.css (linear-gradient, radial-gradient), plus in templates (404.html, portfolio/detail.html, _project_card.html, blog/list.html). Must remove ALL per rule #6. Replace with flat colors.
2. **Gold/yellow tint** — Current accent is gold (#c9a15a/#e8c47a). Must replace with terracotta orange #D97757 (--accent) per new design. Gold appears in buttons, borders, gradients, text gradients, shadows.
3. **Button system inconsistent** — .btn-gold (gradient), .btn-ghost; no .on-cream variant; hover states can lose text contrast. Need unified .btn system per Section 4.
4. **Forms not floating-label** — Current .field has label below input, double border on focus (outline + box-shadow), select dropdown unstyled (white-on-white). Need Material Design outlined field per Section 5.
5. **Section header glyph bug** — .eyebrow uses ::before/::after with gradient lines; .ry-sec-head__glyph shows Persian letter at end of hairline. Must replace with clean eyebrow: orange square + "۰۱ — تماس" per Section 6.
6. **Letter-spacing on Persian** — Multiple letter-spacing rules in CSS (input.css lines 422, 1621, 2311, etc.). Must remove from Persian text per Section 6.
7. **Font sizes too small** — Labels at ~10-11px (ry-label-fa 12px, stat labels 10.5px). Minimum 12px per Section 3.
8. **CTA section not clickable-looking** — Terminal-style panel inside cream band doesn't look interactive. Needs redesign with chips + big button per Section 7.
9. **ASCII-ART-PLACEHOLDER (7 spots)** — 2 on about page, 3 on service detail, 2 on contact page (map SVG). Replace with ASCII canvas per Section 9/10.
10. **Contact page map is SVG animation** — Rotating ellipses/circles (cities-spin). Replace with ASCII globe variant per Section 10.4.
11. **Service pages long & repetitive** — Same grid patterns repeating. Need ASCII visuals + sticky mobile CTA + desktop TOC per Section 11.10.
12. **Stats RTL number/sign issues** — "+" placement inconsistent in RTL. Need <bdi>/dir="ltr" per Section 6.
13. **Large vertical gaps** — Inconsistent section spacing. Unify to padding-block: clamp(72px, 9vw, 128px) per Section 11.6.
14. **Ghost texts overlapping/clipped** — "۱۴۰۵", "SERVICE", "PIXORIA" outline texts. Make decorative, aria-hidden, non-overlapping per Section 11.7.
15. **Preloader uses gradients** — pl-scanlines, pl-noise, pl-matrix use gradients/animations. Must be flat per rule #6.
16. **Footer ghost "PIXORIA" may clash** — Check if it overlaps with pre-footer ASCII band per Section 8.
17. **No ASCII system yet** — Need to build engine.js, scenes, ascii.css, ascii.html partial per Section 9.

## CHECKLIST
- [x] P0.1 Reset progress file (Section 1)
- [x] P0.2 Locate files/tokens, fill DECISIONS
- [x] P0.3 Run site, screenshot pages at 4 widths (use Playwright if available, otherwise inspect templates/CSS and note it)
- [x] P0.4 Write AUDIT list
- [x] P1.1 Add --accent, --accent-ink, --accent-text-on-cream
- [x] P1.2 Remove ALL gradients (CSS + SVG + JS); grep = 0
- [x] P1.3 Fix font-size/contrast floors; remove letter-spacing on Persian
- [x] P1.4 Unify section spacing scale
- [x] P1.5 Replace gold tint with cream/orange. Commit
- [x] P2.1 Create .btn system
- [x] P2.2 Replace every button/CTA usage site-wide
- [x] P2.3 Header button + nav active indicator in orange
- [x] P2.4 Test all states on dark and cream. Commit
- [x] P3.1 .field component (input/textarea/floating label/single border)
- [x] P3.2 Custom select (vanilla JS) + native fallback styling
- [x] P3.3 Apply to contact form and login form; keep Django validation/CSRF
- [x] P3.4 ?service=&plan= prefill
- [x] P3.5 Autofill + error + disabled + loading states. Commit
- [x] P4.1 New eyebrow partial; remove stray letter everywhere
- [x] P4.2 Fix clipped headings
- [x] P4.3 Fix RTL number/sign placement in stats. Commit
- [x] P5.1 engine.js core (grid, loop, observers, reduced motion, HTMX hooks)
- [x] P5.2 Pointer interaction
- [x] P5.3 Scenes: globe, starship, ringed-planet
- [x] P5.4 Scenes: galaxy-fleet, armada-horizon, deep-space-drift
- [x] P5.5 ascii.css + components/ascii.html
- [x] P5.6 Performance check (CPU idle when offscreen, <=30fps). Commit
- [x] P6 — Home hero per 10.1. Commit
- [x] P7 — Home services row per 10.2. Commit
- [x] P8 — CTA redesign + pre-footer band per Sections 7, 8, 10.3 (on every page via base/partials). Commit
- [x] P9 — Replace remaining placeholders — About, Home leftovers, Contact (10.4). grep for ASCII-ART-PLACEHOLDER = 0. Commit
- [ ] P10 — Service pages — 4 pages per 10.5 (one page per sub-step, commit after each)
- [ ] P11 — UI/UX cleanup — go through AUDIT list item by item, tick each. Commit
- [ ] P12 — Final QA per Section 13
- [ ] P1.1 Add --accent, --accent-ink, --accent-text-on-cream
- [ ] P1.2 Remove ALL gradients (CSS + SVG + JS); grep = 0
- [ ] P1.3 Fix font-size/contrast floors; remove letter-spacing on Persian
- [ ] P1.4 Unify section spacing scale
- [ ] P1.5 Replace gold tint with cream/orange. Commit
- [ ] P2.1 Create .btn system
- [ ] P2.2 Replace every button/CTA usage site-wide
- [ ] P2.3 Header button + nav active indicator in orange
- [ ] P2.4 Test all states on dark and cream. Commit
- [ ] P3.1 .field component (input/textarea/floating label/single border)
- [ ] P3.2 Custom select (Alpine) + native fallback styling
- [ ] P3.3 Apply to contact form and login form; keep Django validation/CSRF
- [ ] P3.4 ?service=&plan= prefill
- [ ] P3.5 Autofill + error + disabled + loading states. Commit
- [ ] P4.1 New eyebrow partial; remove stray letter everywhere
- [ ] P4.2 Fix clipped headings
- [ ] P4.3 Fix RTL number/sign placement in stats. Commit
- [ ] P5.1 engine.js core (grid, loop, observers, reduced motion, HTMX hooks)
- [ ] P5.2 Pointer interaction
- [ ] P5.3 Scenes: globe, starship, ringed-planet
- [ ] P5.4 Scenes: galaxy-fleet, armada-horizon, deep-space-drift
- [ ] P5.5 ascii.css + components/ascii.html
- [ ] P5.6 Performance check (CPU idle when offscreen, <=30fps). Commit
- [ ] P6 — Home hero per 10.1. Commit
- [ ] P7 — Home services row per 10.2. Commit
- [ ] P8 — CTA redesign + pre-footer band per Sections 7, 8, 10.3. Commit
- [ ] P9 — Replace remaining placeholders — About, Home leftovers, Contact (10.4). grep for ASCII-ART-PLACEHOLDER = 0. Commit
- [ ] P10 — Service pages — 4 pages per 10.5 (one page per sub-step, commit after each)
- [ ] P11 — UI/UX cleanup — go through AUDIT list item by item, tick each. Commit
- [ ] P12 — Final QA per Section 13