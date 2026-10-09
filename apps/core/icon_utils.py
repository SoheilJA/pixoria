"""Helpers for the local Lucide icon sprites.

Two sprites are generated from the pinned ``lucide-static`` npm package by
``node scripts/build_icon_sprite.js``:

* ``icons/lucide.sprite.svg`` — the PUBLIC sprite: only the icons the site
  actually uses, so the public payload stays small.
* ``icons/lucide.full.sprite.svg`` — the ADMIN-ONLY full sprite (every icon in
  the package plus a few brand glyphs), loaded only on admin pages by the
  ``IconPickerWidget``.

``python manage.py sync_icons`` (T55) rebuilds the public sprite from the icon
values stored in the DB plus every ``{% icon "…" %}`` usage in the templates,
so an admin can pick any Lucide icon and then sync it to the public site.
"""

import re
from functools import lru_cache
from pathlib import Path

from django import forms
from django.conf import settings
from django.contrib.admin import display
from django.core.exceptions import ValidationError
from django.forms.widgets import flatatt
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe

SPRITE_REL_PATH = Path("icons") / "lucide.sprite.svg"
FULL_SPRITE_REL_PATH = Path("icons") / "lucide.full.sprite.svg"
_SYMBOL_RE = re.compile(r'<symbol id="i-([^"]+)"')
DEFAULT_ICON = "sparkles"


def sprite_path(full=False):
    """Absolute path of the sprite inside the static source tree, or ``None``."""
    rel = FULL_SPRITE_REL_PATH if full else SPRITE_REL_PATH
    for base in settings.STATICFILES_DIRS:
        candidate = Path(base) / rel
        if candidate.is_file():
            return candidate
    return None


@lru_cache(maxsize=2)
def available_icons(full=False):
    """frozenset of the icon names found in the sprite (empty if not built yet).

    ``full=True`` reads the admin-only full sprite; the default is the public
    sprite the site actually ships."""
    path = sprite_path(full=full)
    if path is None:
        return frozenset()
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return frozenset()
    return frozenset(_SYMBOL_RE.findall(content))


def validate_icon_name(value):
    """Django field validator — the value must be a real Lucide icon name.

    Validated against the FULL set: an admin may pick any Lucide icon, and
    ``manage.py sync_icons` then adds it to the (small) public sprite. When the
    full sprite is not built yet, nothing is blocked (fresh checkout)."""
    if not value:
        return
    names = available_icons(full=True)
    if not names:
        # Full sprite not built yet (no `npm run build:icons`) — don't block.
        return
    if value not in names:
        raise ValidationError(
            "این نام آیکون در مجموعه Lucide وجود ندارد. "
            "نام انگلیسی آیکون را از https://lucide.dev/icons انتخاب کنید."
        )


def icon_preview_html(name, *, size=22, color="#c9a15a", full=False):
    """اسنیپت SVG یک آیکون لوساید از اسپرایت محلی — برای پیش‌نمایش در ادمین.

    رنگ پیش‌فرض طلاییِ پالت v2 است. ``full=True`` از اسپرایت کامل ادمین
    استفاده می‌کند تا حتی آیکون‌های هنوز-syncنشده هم دیده شوند."""

    if not name:
        return "—"
    rel = FULL_SPRITE_REL_PATH if full else SPRITE_REL_PATH
    url = static(str(rel).replace("\\", "/"))
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
    """ستون «پیش‌نمایش آیکون» را برای مدل‌هایی با فیلد ``icon`` فراهم می‌کند.

    از اسپرایت کامل ادمین استفاده می‌کند تا هر آیکونی که ادمین انتخاب
    کرده دیده شود، حتی اگر هنوز در اسپریت عمومی sync نشده باشد."""

    @display(description="آیکون")
    def icon_preview(self, obj):
        return icon_preview_html(getattr(obj, "icon", "") or getattr(obj, "badge_icon", ""), full=True)


class IconPickerWidget(forms.TextInput):
    """پیکر آیکون: فیلد متنی + پیش‌نمایش زنده + یک جدولِ جستجوپذیر از همهٔ
    آیکون‌های Lucide (فقط ادمین، بدون CDN). کلیدها کار می‌کنند: Escape می‌بندد،
    فلش‌ها جابه‌جا می‌شوند و Enter انتخاب می‌کند."""

    class Media:
        css = {"all": ["admin/css/icon_picker.css"]}
        js = ["admin/js/lucide_full_icons.js", "admin/js/icon_picker.js"]

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs.setdefault("data-ip-input", "")
        return attrs

    def render(self, name, value, attrs=None, renderer=None):
        value = value or ""
        final_attrs = self.build_attrs(self.attrs, attrs)
        input_html = format_html(
            '<input type="text" name="{}" value="{}"{} />',
            name,
            value,
            mark_safe(flatatt(final_attrs)),
        )
        preview = icon_preview_html(value, full=True, size=20)
        sprite_url = static(str(FULL_SPRITE_REL_PATH).replace("\\", "/"))
        return format_html(
            '<div class="icon-picker" data-icon-picker data-ip-sprite="{}">'
            "<div class=\"ip-row\">{}"
            '<button type="button" class="ip-preview" data-ip-preview '
            'aria-label="انتخاب از میان آیکون‌ها" title="انتخاب آیکون">{}</button>'
            "</div>"
            '<p class="ip-warn" data-ip-warn hidden>این آیکون هنوز در اسپریتِ سایت '
            "نیست — دستور <code>python manage.py sync_icons</code> را اجرا کنید "
            "تا روی سایت نمایش داده شود.</p>"
            '<p class="ip-error" data-ip-error hidden>چنین آیکونی در Lucide وجود '
            "ندارد. نام انگلیسی درست را از lucide.dev/icons پیدا کنید.</p>"
            '<div class="ip-popup" data-ip-popup hidden role="dialog" '
            'aria-label="انتخاب آیکون">'
            '<input type="search" class="ip-search" data-ip-search '
            'placeholder="جستجوی آیکون…" autocomplete="off" />'
            '<div class="ip-grid" data-ip-grid></div>'
            '<p class="ip-count" data-ip-count></p>'
            "</div>"
            "</div>",
            sprite_url,
            mark_safe(input_html),
            mark_safe(preview),
        )


class IconPickerForm(forms.ModelForm):
    """فرمِ GENERIC ادمین: فیلد آیکونِ هر مدلی را به ``IconPickerWidget`` وصل
    می‌کند. کافی است ``form = IconPickerForm`` روی ادمینِ یک مدل با فیلد آیکون
    قرار گیرد (Django خودش مدل را در Meta تزریق می‌کند).

    فیلدها را از رویِ مدل تشخیص می‌دهیم (نه از رویِ ولیدیتورهای فرم‌فیلد):
    Django ولیدیتورهای مدل را هنگامِ ساختِ فرم‌فیلد کپی نمی‌کند."""

    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = self._meta.model
        if model is None:
            return
        for field in model._meta.get_fields():
            if not getattr(field, "concrete", False) or field.name not in self.fields:
                continue
            if any(v is validate_icon_name for v in getattr(field, "validators", None) or []):
                self.fields[field.name].widget = IconPickerWidget()
