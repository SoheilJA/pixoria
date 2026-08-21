from django import template

register = template.Library()

STAGGER_BATCH = 6


@register.filter
def stagger(index, step=70):
    try:
        index = int(index)
        step = int(step)
    except (TypeError, ValueError):
        return 0
    return (index % STAGGER_BATCH) * step
