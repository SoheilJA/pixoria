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
