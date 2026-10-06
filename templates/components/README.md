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
(`{% load component_tags %}`). The wrapped markup becomes the scroll-snap track,
so any card partial can be dropped in — this is the only carousel markup and
the only carousel JS in the site:

```django
{% load component_tags %}
{% carousel class='mt-14' %}
  {% for article in articles %}
    {% include 'components/_article_card.html' with article=article %}
  {% endfor %}
{% endcarousel %}
```

| Prop | Type | Default | Notes |
| --- | --- | --- | --- |
| `class` | str | — | extra classes on the wrapper (spacing belongs to the caller) |
| `id` | str | — | wrapper id (anchors/debugging only; the JS never reads it) |

The wrapper carries no config data attributes: the track is plain CSS
`scroll-snap` (`snap-x snap-mandatory`, cards get `snap-start` + a fixed width
from the caller), and `static/js/pixoria.js` `initCarousels` initialises every
`[data-carousel]` per instance — dots (`data-carousel-dots`, one per slide),
prev/next (`data-carousel-prev`/`-next`), keyboard on the focusable track
(`ArrowLeft` advances in RTL, `ArrowRight` goes back, `Home`/`End` jump), and
mouse drag via the shared `enableTrackDrag` helper (touch keeps native scroll).
The dot style is `.slider-dot`, shared with the testimonial slider; `.ctrl-btn`
styles the prev/next buttons. The carousel hides itself when the track is empty
(the section tags below guard on `{% if items %}`).

**Never write real template tag syntax inside a `{# … #}` comment** — the
Django lexer's `tag_re` is not compiled with `re.DOTALL`, so a multi-line
comment is not skipped and the tags inside it are parsed for real (a
self-referencing usage example in a doc comment caused `RecursionError`).
Document usage here in prose instead.

## Cards

v2 card partials — every new page/section MUST use these (props in the file's
header comment):

| Component | Props | Model |
| --- | --- | --- |
| `components/_project_card.html` | `project`, `filter_key`, `radius`, `class`, `style` | `apps.portfolio.Portfolio` |
| `components/_article_card.html` | `article`, `delay`, `class`, `style` | `apps.blog.Article` |
| `components/_testimonial_card.html` | `t`, `class` (text/video/audio kinds inside one partial) | `apps.services.ServiceTestimonial` |

`filter_key` only emits the home grid's filter hook (`pf-item` + `data-cat`).
The staggered values (`radius`, `delay`) come from a `{% cycle ... as x silent %}`
in the caller's loop — `{% cycle %}` inside an `{% include %}` resets on every
inclusion, so the partial cannot generate them itself.

The legacy `components/cards/*.html` cards are v1-styled and remain only for
pages that are not converted yet (`blog/partials/article_cards.html`,
`services/detail.html`); they are deleted in the cleanup phase.

## Section components (inclusion tags)

These run their own query, so a page does not pass the data in context, and
they render nothing when there is no data:

```django
{% load testimonial_tags %}
{% testimonials_slider %}                          {# نظراتِ عمومی (show_on_home) #}
{% testimonials_slider service=object limit=6 %}   {# نظراتِ یک خدمت #}
```

| Tag | Props | Template | Model |
| --- | --- | --- | --- |
| `testimonials_slider` | `service` (default none), `limit` (9), `title`, `eyebrow`, `id` (`"testimonials"`) | `components/testimonials_slider.html` | `ServiceTestimonial` |
| `projects_carousel` | `exclude`, `category` (instance or slug), `service` (Service instance → its title, or string), `limit` (8) | `components/projects_carousel.html` | `apps.portfolio.Portfolio` |
| `articles_carousel` | `exclude`, `category` (instance or slug), `limit` (8) | `components/articles_carousel.html` | `apps.blog.Article` |

Each renders nothing when its query is empty. The two carousels drop into the
`{% carousel %}` shell above; `articles_carousel` backs the home blog section,
and both are meant for related-content blocks on detail pages. `exclude` takes
a model instance (the current object); `limit` is `int()`-coerced so a string
variable cannot 500 the page.

The slider markup uses no element ids: `data-slider` (track), `data-slider-root`
(scope the JS looks the controls up in), `data-slider-prev` / `data-slider-next`
/ `data-slider-dots`, and `.t-card` per slide. `static/js/pixoria.js`
initialises every `[data-slider]` independently, so several sliders may share a
page. Pass a distinct `id` when more than one is on the same page.

## Conventions

- A component never reaches into the parent's context except through its
  documented props (an `{% include %}` with `only` is not used because
  `forloop` is needed by card staggered animations — pass an explicit `index`
  when you need a stable number outside a loop).
- `data-reveal` attributes live on the component root, not the call site.
- Text that can contain rich text uses `|safe`; plain strings do not.
- When a new component lands, add it to this table and to AGENT.md.
