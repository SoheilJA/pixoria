"""Lucide Icons template tag.

Usage:  {% icon "rocket" class="h-6 w-6 text-lime" %}
Renders an inline <svg class="lucide"> that pulls the glyph from the local
sprite (static/lucide/sprite.svg) via <use href="…#name">, so icons are
styleable with currentColor (stroke, text-gold …) and served locally
(no CDN). Lucide sprite is fetched once by the browser and cached.

Since the element is a real SVG, Tailwind sizing utilities (h-6 w-6) work
directly as CSS width/height — every existing call site works unchanged.
When a call site passes no size class at all, the tag sets width/height
to 1em so the glyph scales like the surrounding text did before.

Props:
  name   str  required — Lucide icon name (e.g. "arrow-left"); legacy
              names are mapped automatically
  class  str  optional — CSS classes for the <svg> element
  size   str  optional — explicit width/height (e.g. "20px" or "1.25rem")
"""

import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

from apps.core.icon_utils import available_icons, map_icon_name, sprite_url

register = template.Library()

_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# کلاسی که اندازهٔ صریح می‌دهد: h-6 / w-4.5 / h-[20px] / h-[1.5rem] —
# اما نه h-full و نه h-1/2 (درصد و کلیدواژه؛ مرورگر خودش اعمال می‌کند).
_SIZE_RE = re.compile(
    r"(?:^|\s)(?:h|w)-"
    r"(?:\[[0-9.]+(?:px|rem)\]|[0-9]+(?:\.[0-9]+)?(?![0-9/.-]))"
)
_SIZE_VALUE_RE = re.compile(r"^[0-9.]+(?:px|rem|em|%)?$")


@register.simple_tag
def icon(name, class_name="", size=None, **kwargs):
    # نام‌ها از قالب‌ها (literal) یا دیتابیس (ویرایشِ ادمین) می‌آیند — فقط
    # اسلاگ‌های معتبر قبول می‌شوند و نام‌های قدیمی نگاشت می‌گردند.
    if not name or not _NAME_RE.match(str(name)):
        return ""
    name = map_icon_name(str(name))
    # fail soft: آیکونی که در اسپرایت نیست به جای یک شکلِ نامعتبر هیچ چاپ نمی‌کند.
    available = available_icons()
    if available and name not in available:
        return ""

    cls = class_name or kwargs.get("class", "")

    # اندازه: size صریح ← کلاس h-/w- ← پیش‌فرضِ 1em
    dims = ""
    if size:
        if not _SIZE_VALUE_RE.match(str(size)):
            return ""
        dims = f' width="{size}" height="{size}"'
    elif not _SIZE_RE.search(cls):
        dims = ' width="1em" height="1em"'

    classes = "lucide"
    if cls:
        classes += f" {escape(cls)}"
    return mark_safe(
        f'<svg class="{classes}" aria-hidden="true" focusable="false"'
        ' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
        ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
        f'{dims}><use href="{sprite_url()}#{name}" /></svg>'
    )


@register.simple_tag
def icon_exists(name):
    """True اگر نام آیکون (بعد از نگاشت) در اسپرایتِ محلی موجود باشد."""
    names = available_icons()
    if not names:
        return True  # اسپرایت هنوز خوانده نشده — موقعِ setup اشتباهِ منفی نده
    return map_icon_name(str(name)) in names
