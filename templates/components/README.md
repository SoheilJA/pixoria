# Pixoria template components

Reusable `{% include %}`-able partials. Every file documents its props in a
comment at the top — read that first. Props are passed with `with`:

```django
{% include 'components/section_header.html' with eyebrow='تیم' title='آدم‌های پشت کارها' %}
```

All visitor-facing text is Persian. Classes come from the design tokens in
`static/src/input.css` (see AGENT.md). Do not duplicate markup that already
lives here — extend the component instead.

## Layout / chrome

| Component | Props | Used by |
| --- | --- | --- |
| `components/page_hero.html` | `crumbs`, `title`, `title_id`, `description`, `tags`, `cta_*`, `class` | about, contact, services, portfolio, blog |
| `components/breadcrumb.html` | `items` (list of `{label, url?}`) | page_hero, blog detail hero |
| `components/section_header.html` | `eyebrow`, `title`, `title_id`, `subtitle`, `cta_text`, `cta_href`, `align`, `class` | every section with a heading |
| `components/button.html` | `text`, `href`, `variant` (lime/ink/ghost/ghost-light), `icon`, `icon_after`, `arrow` (left/down), `class`, `id`, `type` | CTAs everywhere |
| `components/badge.html` | `text`, `variant` (line/solid/soft), `href`, `dir`, `class` | tags, categories |
| `components/cta_banner.html` | (none — data from `CTASection` via context processor) | base.html |

## Carousel

`components/carousel.html` + the `{% carousel %}…{% endcarousel %}` block tag
(`{% load component_tags %}`). The wrapped markup becomes the carousel track,
so any card partial can be dropped in — this is the only carousel markup and
the only carousel JS in the site:

```django
{% load component_tags %}
{% carousel id='works-carousel' per_view=4 gap=24 %}
  {% for work in featured_works %}
    {% include 'components/cards/portfolio_card.html' with work=work %}
  {% endfor %}
{% endcarousel %}
```

| Prop | Type | Default | Notes |
| --- | --- | --- | --- |
| `id` | str | — | wrapper id (debugging/anchors only; the JS is id-agnostic) |
| `per_view` | int | 3 | desktop slides per view; 1 on mobile, `min(2, per_view)` on tablet |
| `gap` | int | 24 | px gap between slides |
| `autoplay` | bool | false | auto-advance; disabled under `prefers-reduced-motion` |
| `interval` | int | 6000 | autoplay step in ms (clamped to ≥ 2000) |
| `arrows` | bool | true | prev/next buttons (Lucide arrows) |
| `dots` | bool | true | dot indicators, one per scroll position |
| `class` | str | — | extra classes on the wrapper |

JS: `static/js/core/carousel.js` — a single generic pass initialises every
`.carousel` from its own `data-*` attributes (no per-id config) and re-runs on
`htmx:afterSwap`; carousels replaced by a swap are destroyed so their timers
and listeners do not leak. RTL: the previous button sits on the right and
points right, `ArrowLeft` advances, `ArrowRight` goes back.

**Never write real template tag syntax inside a `{# … #}` comment** — the
Django lexer's `tag_re` is not compiled with `re.DOTALL`, so a multi-line
comment is not skipped and the tags inside it are parsed for real (a
self-referencing usage example in a doc comment caused `RecursionError`).
Document usage here in prose instead.

## Cards (`components/cards/`)

| Component | Props | Model |
| --- | --- | --- |
| `blog_card.html` | `article`, `show_image`, `class` | `apps.blog.Article` |
| `portfolio_card.html` | `work`, `class` | `apps.portfolio.Portfolio` |
| `testimonial_card.html` | `t`, `class` | `ServiceTestimonial` |
| `service_card.html` | `service`, `index`, `class` | `apps.services.Service` |

## Conventions

- A component never reaches into the parent's context except through its
  documented props (an `{% include %}` with `only` is not used because
  `forloop` is needed by card staggered animations — pass an explicit `index`
  when you need a stable number outside a loop).
- `data-aos` reveal attributes live on the component root, not the call site.
- Text that can contain rich text uses `|safe`; plain strings do not.
- When a new component lands, add it to this table and to AGENT.md.
