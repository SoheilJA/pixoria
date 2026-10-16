"""Block-style component tags.

`{% carousel %}…{% endcarousel %}` renders templates/components/carousel.html
and puts the wrapped markup into the `content` slot, so the track can be
filled with any card partial from the call site:

    {% load component_tags %}
    {% carousel class='mt-14' %}
      {% for article in articles %}
        {% include 'components/_article_card.html' with article=article %}
      {% endfor %}
    {% endcarousel %}

Keyword arguments are forwarded to the partial as template context (e.g.
`class`, `id`).
"""

from django import template

register = template.Library()


class CarouselNode(template.Node):
    TEMPLATE = "components/carousel.html"

    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        resolved = {key: value.resolve(context) for key, value in self.kwargs.items()}
        # Render the wrapped markup in the untouched outer context first, so
        # the carousel's own props (e.g. class) never leak into the card
        # partials placed inside the block.
        inner = self.nodelist.render(context)
        with context.push({**resolved, "content": inner}):
            # Resolve to the engine-level Template (like {% include %}):
            # backends.django.Template.render() only accepts a dict, while
            # base.Template.render() takes the live Context and keeps the
            # current request and autoescape state.
            tpl = template.loader.get_template(self.TEMPLATE).template
            return tpl.render(context)


@register.tag(name="carousel")
def do_carousel(parser, token):
    bits = token.split_contents()[1:]
    kwargs = {}
    for bit in bits:
        if "=" not in bit:
            raise template.TemplateSyntaxError(
                f"carousel tag: '{bit}' must be key=value (e.g. per_view=4)"
            )
        key, _, value = bit.partition("=")
        # "true"/"false" read as booleans so callers can write autoplay=true
        if value in ("true", "false"):
            kwargs[key] = template.base.Variable(
                "True" if value == "true" else "False"
            )
        else:
            kwargs[key] = parser.compile_filter(value)
    nodelist = parser.parse(("endcarousel",))
    parser.delete_first_token()
    return CarouselNode(nodelist, kwargs)
