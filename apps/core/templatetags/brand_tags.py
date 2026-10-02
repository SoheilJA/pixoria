"""Pixel wordmark template tags.

Usage:  {% load brand_tags %}
        {% pixel_wordmark "full" class="h-6" %}     → «پیکسوریا», ink (currentColor) + lime accent
        {% pixel_wordmark "mono" class="h-5 text-lime" %}   → monochrome, tinted by CSS
        {% pixel_wordmark "compact" class="h-8" %}  → pixel «پ» mark

Inlines the generated SVG (static/brand/*.svg, built by
scripts/build_pixel_wordmark.py) so the pixels can be animated. When a custom
logo is uploaded through SiteSettings, use it as an <img> instead — see the
header/footer markup in base.html.

Props:
  variant  str  one of full | mono-white | mono-lime | compact (default "full")
  class    str  CSS classes injected onto the <svg> element
"""

from functools import lru_cache
from pathlib import Path

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

VARIANTS = {
    "full": "wordmark-full.svg",
    "mono": "wordmark-mono.svg",
    "compact": "mark-compact.svg",
}


@lru_cache(maxsize=8)
def _read_asset(filename):
    """Raw markup of a generated brand asset, or '' if it cannot be read."""
    for base in settings.STATICFILES_DIRS:
        path = Path(base) / "brand" / filename
        if path.is_file():
            return path.read_text(encoding="utf-8")
    return ""


@register.simple_tag
def pixel_wordmark(variant="full", class_name="", **kwargs):
    filename = VARIANTS.get(variant, VARIANTS["full"])
    svg = _read_asset(filename)
    if not svg:
        return ""
    cls = class_name or kwargs.get("class", "")
    if cls:
        svg = svg.replace("<svg ", f'<svg class="{cls}" ', 1)
    return mark_safe(svg)
