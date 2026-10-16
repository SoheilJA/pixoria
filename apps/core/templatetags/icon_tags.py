"""Font Awesome icon template tag.

Usage:  {% icon "rocket" class="h-6 w-6 text-lime" %}
Renders an inline <i class="fa-solid fa-rocket …"> referencing the local
self-hosted Font Awesome webfont (static/fontawesome/), so icons are
styleable with currentColor and served locally (no CDN).

Icons are fonts, so Tailwind sizing utilities (h-6 w-6) would do nothing on
an inline element — the tag converts them to an inline font-size instead,
which keeps every existing call site working unchanged. Color classes
(text-gold …) pass through untouched because the glyphs use currentColor.

Props:
  name   str  required — Font Awesome icon name (e.g. "arrow-left")
  class  str  optional — CSS classes for the <i> element
  size   str  optional — explicit font-size (e.g. "20px" or "1.25rem")
"""

import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

from apps.core.icon_utils import available_icons, icon_style, map_icon_name

register = template.Library()

_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# h-6 / w-4.5 / h-[20px] / h-[1.5rem]. کسرهای تیلویند (h-1/2) و کلیدواژه‌ها
# (h-full) عمداً تشخیص داده نمی‌شوند: تبدیلِ آنها به font-size ممکن نیست،
# پس بهتر است دست‌نخورده باقی بمانند و مرورگر خودش رویِ عنصر اعمالشان کند.
_SIZE_RE = re.compile(
    r"(?:^|\s)(?:h|w)-"
    r"(?:\[([0-9.]+)(px|rem)\]|([0-9]+(?:\.[0-9]+)?)(?![0-9/.-]))"
)
_DIM_RE = re.compile(
    r"(?:^|\s)(?:h|w)-"
    r"(?:\[[0-9.]+(?:px|rem)\]|[0-9]+(?:\.[0-9]+)?(?![0-9/.-]))"
)


def _font_size_from_classes(cls):
    """اولین کلاسِ اندازهٔ Tailwind (h-N/w-N) را به font-size تبدیل می‌کند."""
    m = _SIZE_RE.search(cls)
    if not m:
        return None
    if m.group(1):  # h-[20px] / h-[1.5rem]
        return f"{m.group(1)}{m.group(2)}"
    return f"{float(m.group(3)) * 0.25}rem"


@register.simple_tag
def icon(name, class_name="", size=None, **kwargs):
    # نام‌ها از قالب‌ها (literal) یا دیتابیس (ویرایشِ ادمین) می‌آیند — فقط
    # اسلاگ‌های معادل قبول می‌شوند و نام‌های قدیمیِ Lucide نگاشت می‌گردند.
    if not name or not _NAME_RE.match(str(name)):
        return ""
    name = map_icon_name(str(name))
    # fail soft: آیکونی که در فونت نیست به جای یک گلیفِ نامعتبر هیچ چاپ نمی‌کند.
    available = available_icons()
    if available and name not in available:
        return ""

    cls = class_name or kwargs.get("class", "")
    font_size = size or _font_size_from_classes(cls)
    cls = _DIM_RE.sub(" ", cls).strip()

    classes = f"fa-{icon_style(name)} fa-{name}"
    if cls:
        classes += f" {escape(cls)}"
    style = f' style="font-size:{escape(font_size)}"' if font_size else ""
    return mark_safe(
        f'<i class="{classes}" aria-hidden="true" focusable="false"{style}></i>'
    )


@register.simple_tag
def icon_exists(name):
    """True اگر نام آیکون در فونتِ محلی وجود داشته باشد (پیش‌نمایش ادمین)."""
    names = available_icons()
    if not names:
        return True  # icons.json هنوز بیلد نشده — موقعِ setup اشتباهِ منفی نده
    return map_icon_name(str(name)) in names
