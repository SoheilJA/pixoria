"""Lucide icon template tag.

Usage:  {% icon "rocket" class="h-6 w-6 text-lime" %}
Renders an inline <svg> that references the local Lucide sprite
(static/icons/lucide.sprite.svg) via <use>, so icons are crisp,
styleable with currentColor and served locally (no CDN).

Props:
  name   str  required — lucide icon name (e.g. "arrow-left")
  class  str  optional — CSS classes for the <svg> element
  size   str  optional — shorthand, sets width/height attributes (e.g. "24")
"""

import re

from django import template
from django.templatetags.static import static
from django.utils.html import escape
from django.utils.safestring import mark_safe

from apps.core.icon_utils import available_icons

register = template.Library()

SPRITE = "icons/lucide.sprite.svg"
_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


@register.simple_tag
def icon(name, class_name="", size=None, **kwargs):
    # Names come from templates (literals) or the DB (admin-edited) — guard the
    # attribute value and drop anything that isn't a valid Lucide slug.
    if not name or not _NAME_RE.match(str(name)):
        return ""
    # Fail soft: an icon that is not (yet) in the public sprite renders nothing
    # instead of a dangling <use> — run `manage.py sync_icons` after picking a
    # new icon in the admin (T55).
    available = available_icons()
    if available and name not in available:
        return ""
    href = f"{static(SPRITE)}#i-{name}"
    cls = class_name or kwargs.get("class", "")
    attrs = 'aria-hidden="true" focusable="false"'
    if size:
        attrs += f' width="{size}" height="{size}"'
    if cls:
        attrs += f' class="{escape(cls)}"'
    return mark_safe(
        f'<svg {attrs} fill="none" stroke="currentColor" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        f'viewBox="0 0 24 24">'
        f'<use href="{href}" xlink:href="{href}"></use></svg>'
    )


@register.simple_tag
def icon_exists(name):
    """True if the icon name exists in the local sprite (used by admin preview)."""
    names = available_icons()
    if not names:
        return True  # sprite not built yet — don't false-negative during setup
    return name in names
