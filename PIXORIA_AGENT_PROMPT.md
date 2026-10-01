# PIXORIA — Master Redesign Prompt for the VS Code AI Agent

> You are an autonomous senior full-stack engineer + creative frontend director working inside VS Code on an existing Django project called **Pixoria (پیکسوریا)**, a Persian (RTL) agency website.
> Read this ENTIRE file before touching any code. Then follow the "Execution Protocol" strictly.
> **All user-facing output (website text, admin labels, placeholders, seed data, messages) MUST be in Persian (فارسی).** Code, comments, variable names, commit messages and `AGENT.md` entries are in English.

---

## 0. Language & Output Rules

- Website content, admin `verbose_name`s, `help_text`s, form labels, default seed texts, preloader texts, error pages → **Persian**.
- Code identifiers, comments, commit messages → **English**.
- The site is **RTL** (`dir="rtl"`, `lang="fa"`). Every layout, animation direction, carousel, icon placement, and scroll-direction detail must be RTL-correct.
- Never leave Lorem ipsum. Write convincing, professional Persian copy for an agency that offers web design/development, branding, social media, SEO, etc. (adapt to the services that already exist in the project).

---

## 1. Project Context (what already exists — PRESERVE IT)

- Backend: **Django** (Django templates are the "frontend engine"). Hosted on Runflare. DB currently SQLite (PostgreSQL planned later — avoid SQLite-only hacks).
- Frontend: **Tailwind CSS**, **GSAP**, **Three.js**, **HTMX**, **Alpine.js**, a custom CSS design system. A hero section already contains a 3D planet model.
- The site is already template-driven: content comes from models and is editable in **Django admin**. A blog app exists (django-tinymce, categories, per-article SEO fields, auto table of contents, HTMX pagination). Pages exist for services, about, portfolio, testimonials, blog, contact, etc.
- Search Console is connected.
- **Before changing anything: audit the whole repo** (apps, models, admin, templates, static, urls, settings, context processors, template tags, JS files, Tailwind config/build process). Write a short summary of the architecture into `AGENT.md` under "Repo Audit".

### Golden rules (never violate)

1. **Do not break existing functionality, URLs, models, migrations, or data.** Existing template-engine usage (`{% extends %}`, `{% include %}`, context data, template tags) must keep working.
2. **Every piece of text or image that appears on any page/section must be editable from Django admin.** If you add a new section or element, you MUST: create/extend a model → add a migration → register it in `admin.py` (with sensible `list_display`, `fieldsets`, inlines, ordering, `help_text` in Persian) → feed it to the template through a view/context processor → provide Persian default content via a data migration or a management command (`seed_pixoria`) so the site is never empty.
3. **No React, Vue, Svelte, Angular or similar frameworks.** Everything else is allowed (vanilla JS, Alpine.js, HTMX, GSAP + ScrollTrigger, Three.js, Lenis, Swiper-like vanilla libs, etc.).
4. **Avoid CDNs as much as possible.** Every library (GSAP, ScrollTrigger, Three.js + any loaders/addons, Lenis, Lucide, HTMX, Alpine, fonts, etc.) must be **downloaded and served locally** from `static/`. Use `npm`/direct download of the dist files, pin versions, and note them in `AGENT.md`. Fonts must be self-hosted (`@font-face`, woff2, `font-display: swap`, subset if possible). If a CDN is truly unavoidable, document why in `AGENT.md`.
5. Keep performance in mind: lazy-load heavy things, respect `prefers-reduced-motion`, pause WebGL when the tab is hidden, cap device pixel ratio, provide graceful fallbacks on weak devices/mobile.
6. Accessibility basics: focus states, aria labels on icon buttons, sufficient contrast on glass surfaces, keyboard-operable carousels/menus.

---

## 2. Execution Protocol (VERY IMPORTANT)

1. **Create a file named `AGENT.md` in the project root first.** It must contain:
   - The Repo Audit summary.
   - A checklist of ALL tasks below, **ordered from the simplest to the most complex**, each with a checkbox: `- [ ] Task`.
   - A "Decisions & Notes" section (library versions, new models, conventions) and a "Known Issues / Follow-ups" section.
2. Work **step by step**, one task (or one tight group of tasks) at a time, in the order of the checklist.
3. After finishing each task: run the project (`python manage.py check`, makemigrations/migrate if needed, test the pages you touched), **tick the checkbox** in `AGENT.md` (`- [x]`), and then **make a git commit** with a **short, summarized English message** (imperative mood, ≤ 72 chars, e.g. `Add pixel wordmark logo and remove P favicon`). One commit per finished step. Do not squash everything at the end.
4. After each major visual step, **re-align the other pages** (inner pages, blog, contact, 404, etc.) with the new global design so the site stays consistent at every commit.
5. If a task is ambiguous, choose the most premium, most consistent option and write the decision in `AGENT.md` — do not stop to ask unless something is destructive.
6. You may **add extra improvements** that make the site feel more premium (list them in `AGENT.md` under "Extras I Added"), as long as they respect the golden rules.
7. At the end, do a full QA pass (see Section 14) and commit `Final QA and polish`.

---

## 3. Design Vision (the north star)

**Feel:** premium, luxurious, cinematic, "agency from the future". Think deep-space + liquid glass + emerald-green glow, with refined typography and generous spacing. It should feel expensive, calm, and alive — not noisy.

- **Theme: fully dark, everywhere.** Remove all light-theme remnants (backgrounds, cards, forms, tables, prose/blog content, admin-driven rich text, 404/500 pages). Base surfaces are near-black with a very subtle cool/green tint (not pure #000 everywhere; use layered depth: `--bg-0`, `--bg-1`, `--bg-2`).
- **Accent color: use the CURRENT primary green already in the project** (find it in the Tailwind config / CSS variables and reuse it — do not invent a new hue). Derive a full scale from it (50–950), a glow color, a soft translucent variant for glass borders/highlights, and a gradient (primary → slightly lighter/cyan-shifted tone). Use it consistently for: buttons, links, active states, icons, borders on hover, section highlights, glows, focus rings, progress bars, selection color, scrollbar.
- **Define a real design system** with CSS variables + Tailwind theme extension: colors, radii, shadows/glows, blur levels, spacing rhythm, z-index scale, easing curves, durations. Document the tokens in `AGENT.md`.
- **Typography:** keep the current Persian font if it is good; otherwise self-host a modern Persian font (e.g. Vazirmatn / Estedad / IRANYekan-like licensing permitting). Strong hierarchy, large elegant headings, comfortable line-height for Persian body text, Persian digits where appropriate.
- **Consistency:** every page uses the same header, footer, section rhythm, glass cards, buttons, headings style, and motion language.

### Glass & Liquid Glass

Build reusable utility/component classes (in Tailwind `@layer components` or a CSS file) such as `.glass`, `.glass-strong`, `.glass-card`, `.liquid-glass`:

- `backdrop-filter: blur() saturate()`, translucent gradient backgrounds, 1px inner highlight borders (top-left brighter), soft outer shadow + faint green glow on hover.
- **Liquid glass** variant: subtle SVG displacement/refraction filter (`feTurbulence` + `feDisplacementMap`) or layered specular highlights, a moving light reflection that follows the cursor, rounded blobby shapes. Provide a graceful fallback (plain frosted glass) for browsers without support (check `@supports`), and don't apply heavy filters to huge areas (performance).
- Use glass for: header, mobile menu, cards, carousels, forms, modals, buttons, badges, footer panels, preloader elements.
- **Readability first:** because the background is a space scene, every text container needs enough glass/dark scrim so Persian text stays highly legible (WCAG AA contrast).

---

## 4. Global 3D Space Background + Scroll Journey (CORE FEATURE)

### 4.1 Hero

- The hero already has a 3D planet exactly in the center. **Move it toward the left** (the text is on the right in RTL). Keep it responsive: on mobile, place the planet behind/above the text, smaller, and dimmer.
- Make the planet richer: atmosphere glow (fresnel shader) in the brand green, slow rotation, subtle cloud/ring layer if cheap, a soft lens-flare/starlight, gentle mouse parallax.
- Add a starfield (2–3 parallax layers of points), occasional shooting stars, very light nebula/gradient dust tinted with the brand green.

### 4.2 Scroll = Travelling through space

- Convert the Three.js scene into **one fixed, full-viewport canvas behind the whole site** (`position: fixed; inset: 0; z-index: -1`, `pointer-events: none`). Content sits above it.
- Tie the camera to **scroll progress** (GSAP ScrollTrigger scrub, optionally smoothed by Lenis — served locally). As the user scrolls, the camera **flies forward through space**: passes the hero planet, then other planets, moons, asteroid fields, rings, glowing stars, nebula clouds, a distant galaxy/portal near the footer. Each major page section should correspond to a different "region of space" (different dominant planet/color temperature, always harmonious with the green brand color).
- The journey must be **subtle, not distracting**: apply a dark gradient overlay/vignette ("halo") over the scene so text is always readable; reduce brightness and blur far objects slightly; keep motion smooth and slow; avoid anything flashing.
- Planets can be procedurally generated (noise shaders / textures generated at runtime or small local textures) to avoid heavy downloads. Keep total extra assets small and local.
- **HTMX-aware:** the canvas/scene must live in the persistent layout (outside the swapped target) so it is **not re-created on page transitions**. On page change, animate the camera to a new "position" for that page (e.g. each page has its own region/offset) and recompute the scroll range (`ScrollTrigger.refresh()`) after the swap. Inner pages use a calmer version of the scene.
- Performance: dispose geometries/materials properly, cap DPR (≈1.5–2), reduce particle counts on mobile/low-end (`navigator.hardwareConcurrency`, `deviceMemory`), pause rendering when the tab is hidden or the canvas is fully covered, and fall back to a static CSS starfield + gradient when WebGL is unavailable or `prefers-reduced-motion` is on.

---

## 5. Motion & Interaction Language (scroll + hover everywhere)

The whole site must react to scrolling and hovering in interesting, premium ways. Build a small reusable motion layer (e.g. `static/js/motion.js`) driven by `data-*` attributes so templates stay clean (e.g. `data-reveal="up"`, `data-parallax="0.2"`, `data-tilt`, `data-magnetic`, `data-split`, `data-counter`).

**Scroll effects (mix, don't overuse):**

- Staggered reveals (fade/translate/blur-in), text split reveals for headings (Persian-safe: split by words, NOT by letters, to avoid breaking Arabic-script joining!), clip-path/mask reveals for images.
- Parallax layers, pinned/sticky storytelling sections, horizontal scroll sections, number counters, progress lines that draw along with scroll, scroll-linked color/glow shifts.
- A slim scroll progress bar (brand green) in the header.

**Hover effects:**

- Cards: 3D tilt with glare following the cursor, border-glow that tracks the pointer, icon micro-animations.
- Buttons: magnetic pull, shine sweep, liquid-fill, arrow slide (RTL-correct).
- Links: animated underline; images: slight zoom + overlay reveal; custom soft cursor follower on desktop only (disabled on touch).
- Everything must degrade gracefully on touch devices and under `prefers-reduced-motion`.

---

## 6. Header & Mobile Menu (currently bad → rebuild)

- Rebuild the **header** from scratch: floating glass pill/bar that is transparent at the top and becomes denser glass on scroll, hides on scroll-down and reappears on scroll-up (or shrinks), with the pixel wordmark logo, nav links with animated active indicator (a sliding glowing pill), a primary CTA button (e.g. "درخواست پروژه"), and a scroll progress line.
- **Services dropdown / mega-menu** (glass) listing service pages with Lucide icons and short descriptions — items must come from the database (services model), not hardcoded.
- **Mobile menu:** a full-screen (or slide-over) liquid-glass overlay with a staggered link reveal, large touch targets, an animated hamburger → close morph, the contact buttons/social links at the bottom, space-themed ambient animation behind it, scroll-lock while open, focus trap + ESC to close, and it must close automatically after an HTMX navigation.
- Header menu items/labels/CTA text/social links must be editable via admin (use the existing menu/settings models if they exist; otherwise create a `SiteSettings` singleton + `MenuItem` model).

---

## 7. Logo & Branding

- The current site icon is a **"P"** — **remove it everywhere** (favicon, header, footer, preloader, `manifest`, Open Graph/Twitter images, apple-touch-icon, admin branding).
- The site name **«پیکسوریا»** must be rendered as a **pixel-style wordmark** and used as the logo everywhere. Implementation: create it as an **inline/standalone SVG** built from a pixel grid (each Persian letter drawn with square "pixels", crisp edges via `shape-rendering: crispEdges`), in white with the brand green accent on some pixels/one letter; add a subtle pixel "glitch/assemble" animation on hover and on preloader. Provide variants: full wordmark (header/footer/preloader), compact wordmark, monochrome. Alternatively, use a locally hosted pixel-style Persian display font if one exists with a proper license — but the SVG approach is preferred for reliability.
- Generate a **new favicon set** from the wordmark/compact pixel mark (NOT a "P"): `favicon.ico`, 16/32/48/192/512 PNGs, `apple-touch-icon.png`, `site.webmanifest`, and an SVG favicon. Note: Google requires the favicon to be a multiple of 48×48 px — ensure a ≥48×48 icon is linked in `<head>`. Store them in `static/` and make the logo/favicon **replaceable from admin** (ImageField/FileField on `SiteSettings`) with the generated files as defaults.

---

## 8. Reusable Components (React-like thinking in Django templates)

I want to write a UI piece **once** and reuse it everywhere, like a React component. Implement this with Django's template system:

- Create `templates/components/` with `{% include %}`-able partials accepting parameters via `with` (or custom `{% simple_tag %}` / `{% inclusion_tag %}` templatetags with a typed, documented signature). Document every component's props at the top of its file in a comment.
- **Carousel component** (one single implementation) used for: **portfolio items, testimonials, blog posts**, and anywhere else (related posts, services, team…). Props example: `items`, `item_template` (which card partial to render), `autoplay`, `slides_per_view` (responsive), `show_arrows`, `show_dots`, `loop`, `title`, `subtitle`, `cta`. Its JS must be one vanilla/Alpine module with: RTL support, touch drag/inertia, keyboard and a11y, autoplay with pause on hover, snap, progress indicator, responsive breakpoints, and HTMX-safe re-initialization (`htmx:afterSwap` / `htmx:load`).
- Card partials: `cards/portfolio_card.html`, `cards/testimonial_card.html`, `cards/blog_card.html`, `cards/service_card.html`, … all in the same glass style.
- Other shared components: `section_header` (eyebrow + title + subtitle), `glass_card`, `button` (variants), `badge`, `icon` (Lucide wrapper), `cta_banner`, `stats_counter`, `faq_accordion`, `timeline`, `feature_grid`, `process_steps`, `marquee`, `form_field`, `pagination`.
- Refactor the existing pages to use these components so duplicated markup disappears. Editing a component once must update all places.

---

## 9. Icons — Lucide

- Self-host **Lucide** (download the icon set / the lucide JS or an SVG sprite into `static/`; no CDN). Create an `{% icon "name" class="..." %}` template tag (inline SVG from a local sprite or files) so icons are crisp, styleable with `currentColor`, and usable in templates.
- **Find and replace every icon that is currently an HTML entity / emoji / character code** (e.g. `&#...;`, `&hearts;`, unicode symbols, emoji used as icons) with proper Lucide icons. Grep the whole project (templates, JS strings, admin help texts, model choices that render icons).
- If icons are stored per-item in the database (e.g. a service has an icon field), change the field to hold a **Lucide icon name** (CharField with a Persian `help_text` + a link to the Lucide name list, ideally with a small admin preview) and migrate existing values to sensible Lucide equivalents.

---

## 10. Pages

### 10.1 Home

Rebuild the home page sections with premium, varied layouts (not simple boxes): hero (planet left, text right, animated headline, 2 CTAs, trust stats), logos/marquee, services (bento grid with hover reveals), process/timeline (scroll-drawn line), portfolio carousel (component), why-us (pinned/sticky storytelling or horizontal scroll), stats counters, testimonials carousel (component), blog carousel (component), FAQ, final CTA with a "portal/warp" effect, footer. Each section must have **admin-editable** title/subtitle/body/images/buttons (create `HomeSection`-style models or extend existing ones; use inlines for repeatable items; add `is_active` + `order` fields so sections can be shown/hidden/reordered).

### 10.2 Service pages (expand + individualize)

- Expand the existing service pages and **design each service page specifically for its service**, using visual elements and metaphors that belong to that service. Examples (adapt to the real services in the DB): website design → browser/device mockups, wireframe-to-final animation, responsive device morph; SEO → rising graph, Google-SERP mock, keyword chips; social media → feed/post cards, like/comment float animations; branding/graphic design → color swatches, type specimens, logo grid; video/production → film strip/timeline/play button; app/development → code-window typing effect, architecture diagram. Each page gets a unique hero visual (CSS/SVG/Three.js lightweight), its own sections (what we do, deliverables, process, pricing/packages if relevant, tech/tools, mini case studies from portfolio, FAQs, CTA).
- Make these sections **data-driven**: a `Service` model plus related models/inlines (`ServiceFeature`, `ServiceProcessStep`, `ServiceFAQ`, `ServicePackage`, `ServiceGalleryImage`, etc.), with per-service `layout_variant`/`theme` choices where it helps. Everything editable in admin. You may create new sections freely, but each text/image in them must come from the admin.
- Each service page has its own SEO fields (title, meta description, OG image) and structured data (`Service` schema).

### 10.3 About page

Make it **much longer and richer** with many different section styles: story/vision hero, mission & values (interactive cards), animated timeline of milestones, team grid (hover reveal, social links), numbers/achievements counters, working-method/process section, tech & tools marquee, culture/gallery masonry, testimonials carousel (component), awards/certificates, FAQ, CTA. All admin-editable with inlines (`AboutSection`, `TeamMember`, `Milestone`, `Value`, etc.).

### 10.4 All other pages

Portfolio list/detail, blog list/detail, contact, FAQ, terms, 404/500, etc. must be re-aligned to the new dark/glass/space design and use the shared components. Keep the blog features (TinyMCE content styled for dark theme, auto TOC, HTMX pagination, categories, SEO fields). Style `prose`/rich-text content for dark mode with beautiful typography (code blocks, quotes, tables, images with captions).

### 10.5 Footer

Premium glass footer with the pixel wordmark, short about text, link columns, contact info, social icons (Lucide/brand SVG, local), newsletter/CTA if relevant, and a subtle "end of the universe" visual. Editable from admin.

---

## 11. Preloaders (two different ones)

### 11.1 First-visit preloader (full load)

- Shown only on the **first full page load of a session** (use `sessionStorage`/cookie flag; do not show on every reload within the session unless configured).
- Visual: dark screen, the pixel wordmark "پیکسوریا" assembling pixel by pixel in green/white, a thin progress line/percentage tied to the **real** loading progress (fonts + critical assets + Three.js scene ready), then a cinematic exit: the screen "warps" or the glass panels split open revealing the planet/hero with the hero intro animation starting right after.
- Must not block the site for long: cap the minimum/maximum time (≈1.2s–3s), skip instantly for returning visitors in the same session, and avoid layout shift. Add a `<noscript>` fallback so content is never hidden without JS.

### 11.2 Page-transition preloader (HTMX navigation)

- The site uses **HTMX** for navigation between pages after the initial load. On `htmx:beforeRequest` / `htmx:beforeSwap` / `htmx:afterSettle` (use `hx-boost`/`hx-target`/`hx-push-url` already in the project — inspect and reuse), show a **lighter, faster transition**: e.g. glass panels sweeping across the screen with a mini pixel mark/progress, a quick warp of the space background (camera dash), then reveal the new page.
- **This second preloader must be editable (customizable) from the admin panel.** Create a singleton `PreloaderSettings` model (admin-registered, with `help_text` in Persian) containing at least: `is_enabled` (on/off), `style` (choices, e.g. panels / fade / warp / pixel-dissolve / minimal), `duration_ms`, `show_logo`, `show_text` + `text` (Persian, e.g. «در حال سفر به صفحه بعد…»), `show_progress`, `background_opacity`/`accent_color` (defaults to brand green), `first_load_enabled` (toggle for the first preloader), and an optional random pool of Persian "tips/quotes" shown during the transition. Expose these values to the front end via a context processor + `data-*` attributes/JSON script on `<body>`, and make the JS read them (no hardcoded values).
- Make it robust: no flicker on fast responses (minimum visible time so it doesn't flash, but never delay more than the configured duration), handle errors/timeouts (`htmx:responseError`, `htmx:sendError`), browser back/forward (history restore), anchors, and ensure scroll position/ScrollTrigger/Three.js camera/carousels/icons are re-initialized after swaps.

---

## 12. SEO — Fix "pages appear as separate results in Google"

Problem: in Google search the site's pages are shown individually, and it isn't clear they belong to one website. Fix everything that helps Google understand **one site, one brand**:

1. **Site name & brand signals:** add JSON-LD on every page: `WebSite` (with `name: "پیکسوریا"`, `alternateName` e.g. ["Pixoria", "pixoria.ir"], `url`, `inLanguage: "fa-IR"`, `publisher`), plus `Organization` (name, url, logo, sameAs social links, contactPoint). Also add `SearchAction` only if the site has a real search.
2. **Consistent titles:** every page `<title>` uses a consistent pattern like `عنوان صفحه | پیکسوریا`; the home page title leads with the brand (`پیکسوریا | …`). Unique meta descriptions per page. Titles/descriptions come from admin SEO fields with sensible fallbacks.
3. **`og:site_name`, `og:locale` (fa_IR), `og:type`, `og:url`, `og:image`**, Twitter cards, `<link rel="canonical">` (absolute URL, no query junk), `<html lang="fa" dir="rtl">`.
4. **BreadcrumbList** JSON-LD + visible breadcrumb component on inner pages (service, blog post, portfolio detail, etc.) so Google shows the site hierarchy.
5. **Proper favicon** (see Section 7) linked in `<head>` with a ≥48×48 icon — Google uses it next to the site name in results.
6. **Sitemap & robots:** use `django.contrib.sitemaps` with all indexable models (pages, services, blog posts, categories, portfolio items) with `lastmod`; `robots.txt` pointing to the sitemap; `noindex` on admin/search/utility pages.
7. **HTMX-safe SEO:** every URL must also work as a **full standalone page** when requested directly (not only as a partial). Ensure HTMX partial responses update `<title>`, meta description, canonical and JSON-LD on swap (e.g. `hx-swap-oob` or head-support), and that `hx-push-url` keeps real, crawlable URLs. Internal navigation must use real `<a href>` links (crawlable) enhanced by HTMX, not JS-only navigation.
8. **Internal linking & structure:** clear header/footer navigation, consistent URL structure, hub pages linking to children (services hub → service pages, blog → posts), related-posts/services blocks.
9. Performance basics that affect ranking (Core Web Vitals): image `width/height`, lazy loading, `fetchpriority` for LCP image, no layout shift from the preloader, deferred JS.
10. Write a short "SEO Notes" section in `AGENT.md` explaining what was done and what I should do manually in Search Console afterwards (submit sitemap, request re-indexing of the home page, check "Site name" structured data in the Rich Results Test, wait for Google to recrawl).

---

## 13. Task Checklist (copy this into `AGENT.md`; ordered simple → complex)

Create the checklist in `AGENT.md` exactly in this order (you may add small extra tasks, but keep the order logic: easy and safe first, big and risky last). **Commit after each item.**

- [ ] 1. Repo audit + create `AGENT.md` (architecture summary, checklist, conventions)
- [ ] 2. Vendor all libraries locally (GSAP + ScrollTrigger, Three.js + needed addons, Lenis, HTMX, Alpine, Lucide, fonts) into `static/`; remove CDN links; verify the site still works
- [ ] 3. Design tokens + global dark theme using the existing primary green (CSS variables + Tailwind config); fix every light-theme leftover
- [ ] 4. Lucide icon system (`{% icon %}` tag) + replace all HTML-entity/emoji icons + icon-name fields in models/admin
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
- [ ] 23. Full QA pass: `manage.py check`, migrations, admin editability audit (every visible text/image editable), RTL audit, mobile audit, Lighthouse-style performance check, console errors, HTMX navigation (back/forward, direct URL, refresh), reduced-motion, no-JS fallback, no remaining CDN links, no remaining entity icons → final commit `Final QA and polish`

---

## 14. Definition of Done

- The whole site is dark with the existing green as the primary accent, premium and consistent on every page.
- The planet sits left in the hero; scrolling flies the user through a subtle, readable space journey that persists across HTMX navigation.
- Glass/liquid-glass is used throughout; hover and scroll interactions feel rich but not noisy; performance is solid on mobile.
- Carousels (portfolio, testimonials, blog) use **one** reusable component.
- Header and mobile menu are redesigned and attractive; Lucide icons everywhere; no entity/emoji icons left.
- Pixel-style «پیکسوریا» wordmark is the logo; the "P" is gone from everywhere; new favicon set exists.
- First-visit preloader + editable HTMX transition preloader both work flawlessly.
- Service pages are expanded and individually designed; the About page is long, rich, and varied.
- **Every text and image of every section is editable from Django admin**; every new model is migrated and registered with a good admin UX; default Persian content is seeded.
- Libraries are served locally (no CDN unless justified in `AGENT.md`).
- SEO structure makes Google understand all pages belong to one site (Pixoria), with a sitemap, JSON-LD, canonical, consistent titles, breadcrumbs, and favicon.
- `AGENT.md` shows every checkbox ticked, with one short English commit per step in git history.

**Now start: create `AGENT.md` (Task 1), then proceed step by step. Remember — Persian output for everything the visitor or admin sees, English for code, comments and commits.**
