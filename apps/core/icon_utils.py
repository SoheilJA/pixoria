"""Helpers for the local Lucide icon sprite.

The sprite (``static/icons/lucide.sprite.svg``) is generated from the pinned
``lucide-static`` npm package by ``node scripts/build_icon_sprite.js``. These
helpers let models and admin validate and preview icon names without any CDN.
"""

import re
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.admin import display
from django.templatetags.static import static
from django.utils.html import format_html

SPRITE_REL_PATH = Path("icons") / "lucide.sprite.svg"
_SYMBOL_RE = re.compile(r'<symbol id="i-([^"]+)"')
DEFAULT_ICON = "sparkles"


def sprite_path():
    """Absolute path of the sprite inside the static source tree, or ``None``."""
    for base in settings.STATICFILES_DIRS:
        candidate = Path(base) / SPRITE_REL_PATH
        if candidate.is_file():
            return candidate
    return None


@lru_cache(maxsize=1)
def available_icons():
    """frozenset of the icon names found in the sprite (empty if not built yet)."""
    path = sprite_path()
    if path is None:
        return frozenset()
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return frozenset()
    return frozenset(_SYMBOL_RE.findall(content))


def validate_icon_name(value):
    """Django field validator — the value must exist in the local Lucide sprite."""
    names = available_icons()
    if not names:
        # Sprite not built/collected yet — don't block saves during setup.
        return
    if value not in names:
        raise ValidationError(
            "این نام آیکون در مجموعه Lucide وجود ندارد. "
            "نام انگلیسی آیکون را از https://lucide.dev/icons انتخاب کنید."
        )


def icon_preview_html(name, *, size=22, color="#c9a15a"):
    """اسنیپت SVG یک آیکون لوساید از اسپرایت محلی — برای پیش‌نمایش در ادمین.

    رنگ پیش‌فرض طلاییِ پالت v2 است."""
    if not name:
        return "—"
    url = static(str(SPRITE_REL_PATH).replace("\\", "/"))
    return format_html(
        '<svg aria-hidden="true" width="{}" height="{}" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" style="color:{}">'
        '<use href="{}#i-{}" xlink:href="{}#i-{}"></use></svg>',
        size,
        size,
        color,
        url,
        name,
        url,
        name,
    )


class IconPreviewMixin:
    """ستون «پیش‌نمایش آیکون» را برای مدل‌هایی با فیلد ``icon`` فراهم می‌کند."""

    @display(description="آیکون")
    def icon_preview(self, obj):
        return icon_preview_html(getattr(obj, "icon", ""))
