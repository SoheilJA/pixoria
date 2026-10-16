"""JSON template filter — safe JSON-LD values in templates.

Structured-data blocks need Python values as JSON literals. Escaping the
value first keeps a quote or ``</script>`` inside user content from breaking
out of the script tag::

    "name": {{ portfolio.title|striptags|json }},

The filter returns a marked-safe string because ``json.dumps`` output is
already valid JSON; without ``mark_safe`` Django would escape the quotes and
produce broken JSON.
"""

import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="json", is_safe=True)
def json_filter(value):
    """Serialize a value as a JSON literal for use inside a script tag.

    Args:
        value: any JSON-serializable value (usually a string).

    Returns:
        Marked-safe JSON, e.g. ``"فروشگاه آنلاین"``
        (``ensure_ascii=False`` keeps Persian readable instead of \\uXXXX).
    """
    if value is None:
        return mark_safe("null")
    try:
        return mark_safe(json.dumps(str(value), ensure_ascii=False))
    except (TypeError, ValueError):
        return mark_safe('""')
