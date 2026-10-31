"""Highlight template filters — colored words inside headings.

The V2 design marks one word (or phrase) of a heading with the gold gradient.
Admins write the heading as plain text and wrap the colored part in
double square brackets::

    ما برای رشد کسب‌وکار شما [[طراحی]] می‌کنیم

Usage in templates::

    {{ section.title|highlight }}          → text-goldgrad (dark backgrounds)
    {{ section.title|highlight:"dark" }}   → text-goldgrad-dark (light backgrounds)
    {{ section.title|plain }}              → markers removed (plain text)

Use ``plain`` (not ``highlight``) wherever the text is not rendered as HTML:
``<title>``, meta/OG tags, breadcrumbs, ``alt``/``aria-label``, JSON-LD and
share URLs. Otherwise the raw ``[[…]]`` brackets end up in front of the
visitor. The text is escaped first, so a marker can never inject markup.
Multiple markers in one heading are supported; text without a marker renders
as-is.
"""

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

from apps.core.text_utils import MARKER_RE, strip_highlight

register = template.Library()

_VARIANTS = {
    "": "text-goldgrad",
    "gold": "text-goldgrad",
    "dark": "text-goldgrad-dark",
}


@register.filter(name="highlight")
def highlight(value, variant=""):
    """Convert ``[[…]]`` markers into gold-gradient spans.

    Args:
        value: raw text from the database.
        variant: ``""``/``"gold"`` for dark backgrounds, ``"dark"`` for light
            backgrounds.
    """
    if not value:
        return ""
    cls = _VARIANTS.get(variant, _VARIANTS[""])

    def _wrap(match):
        return f'<span class="{cls}">{escape(match.group(1))}</span>'

    return mark_safe(MARKER_RE.sub(_wrap, escape(str(value))))


@register.filter(name="plain")
def plain(value):
    """Remove ``[[…]]`` markers, keeping the inner text.

    For every plain-text context: ``<title>``, meta/OG tags, breadcrumbs,
    ``alt``/``aria-label``, JSON-LD, share URLs. Marker-free text is returned
    unchanged.
    """
    return strip_highlight(value)
