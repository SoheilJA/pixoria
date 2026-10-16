"""Highlight template filter — colored words inside headings.

The V2 design marks one word (or phrase) of a heading with the gold gradient.
Admins write the heading as plain text and wrap the colored part in
double square brackets::

    ما برای رشد کسب‌وکار شما [[طراحی]] می‌کنیم

Usage in templates::

    {{ section.title|highlight }}          → text-goldgrad (dark backgrounds)
    {{ section.title|highlight:"dark" }}   → text-goldgrad-dark (light backgrounds)

The text is escaped first, so a marker can never inject markup. Multiple
markers in one heading are supported; text without a marker renders as-is.
"""

import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

_MARKER_RE = re.compile(r"\[\[(.+?)\]\]")

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

    return mark_safe(_MARKER_RE.sub(_wrap, escape(str(value))))
