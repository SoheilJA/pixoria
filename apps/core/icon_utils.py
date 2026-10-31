"""پشتیبانی آیکونِ Lucide (اسپرایتِ SVGِ محلی) برای ادمین و قالب‌ها.

کاملاً لوکال: اسپرایتِ ``static/lucide/sprite.svg`` (lucide-static v0.544)
به صورت شناور است و تگ‌ها با ``<svg><use href="…#name">`` از آن برداشت
می‌کنند — بدون وبفونت و بدون CDN. فهرستِ نام‌ها هنگامِ اجرا از خودِ
اسپرایت خوانده می‌شود، پس هر آیکونی که ادمین انتخاب کند فوراً روی سایت
نمایش داده می‌شود و برای سینک چیزی لازم نیست. اسکریپتِ
``scripts/build_lucide_icons.py`` فقط لیستِ جاوااسکریپتِ ادمین
(``static/admin/js/lucide_icons.js``) را از همان اسپرایت تولید می‌کند.

رندرِ `<svg class="lucide">` با ``stroke="currentColor"`` است؛ رنگ/اندازه
با همان کلاس‌های Tailwind (text-gold و h-6 w-6) کنترل می‌شود.
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

SPRITE_REL_PATH = "lucide/sprite.svg"
ADMIN_LIST_JS = "admin/js/lucide_icons.js"
DEFAULT_ICON = "sparkles"
_SYMBOL_RE = re.compile(r'<symbol id="([a-z0-9][a-z0-9-]*)"')

# نام‌های قدیمیِ DB/قالب (سبکِ قدیمیِ Lucide و نوشتارِ فا) به معادلِ
# امروزیِ Lucide و штوارِ خودکار. نام‌هایی که عیناً در اسپرایت موجودند
# (مثل arrow-left، palette، bolt) نیازی به ورود ندارند و خودکار عبور
# می‌کنند؛ این جدول فقط پرش‌ها را پوشش میدهد و
# scripts/build_lucide_icons.py وجودِ مقصدها را در برابر اسپرایت
# اعتبارسنجی می‌کند.
LEGACY_ALIASES = {
    # قالب‌ها
    "alert-circle": "circle-alert",
    "alert-triangle": "triangle-alert",
    "comment": "message-circle",
    "table-cells-large": "layout-grid",
    "up-right-from-square": "square-arrow-up-right",
    # رکوردهای DB با نام‌های سبک‌شودهٔ قدیمی
    "at": "at-sign",
    "box-multiple": "boxes",
    "brand-figma": "figma",
    "building-store": "store",
    "buildings": "building-2",
    "components": "component",
    "confetti": "party-popper",
    "device-mobile": "smartphone",
    "devices-2": "monitor-smartphone",
    "layout-sidebar": "panel-left",
    "movie": "clapperboard",
    "mood-smile": "smile",
    "news": "newspaper",
    "refresh": "refresh-cw",
    "rosette-discount-check": "badge-check",
    "shape-3": "shapes",
    "sitemap": "network",
    "source-code": "code-xml",
    "speakerphone": "megaphone",
    "template": "layout-template",
    "typography": "type",
}

DEFAULT_ICON = "sparkles"

_SVG_OPEN = (
    '<svg class="lucide{cls}" aria-hidden="true" focusable="false"'
    ' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"{dims}>'
)


@lru_cache(maxsize=1)
def sprite_url():
    """URL اصلیِ اسپرایت (با هشِ collectstatic در حالتِ `production`)."""
    return static(SPRITE_REL_PATH)


@lru_cache(maxsize=1)
def available_icons(full=False):
    """frozenset از نام‌های آیکون‌های اسپرایتِ محلیِ Lucide.

    فرمت ``full`` برای سازگاری با کدِ قدیمیِ نگه داشته شده و اثری ندارد.

    وقتی اسپرایت هنوز در دسترس نباشد (fresh checkout ناقص)، خروجی خالی است
    و پس ولیدینگ و رندر هیچ چیز مسدود نمی‌شوند (fail-soft)."""

    for base in settings.STATICFILES_DIRS:
        candidate = Path(base) / SPRITE_REL_PATH
        if candidate.is_file():
            try:
                svg = candidate.read_text(encoding="utf-8")
                return frozenset(_SYMBOL_RE.findall(svg))
            except (OSError, UnicodeDecodeError):
                pass
    return frozenset()


def map_icon_name(name):
    """تبدیل یک نامِ قدیمی به معادلِ امروزیِ Lucide آن."""
    return LEGACY_ALIASES.get(str(name), str(name))


def validate_icon_name(value):
    """ولیدیتورِ فیلدِ آیکون — بعد از نگاشت باید در اسپرایت موجود باشد.

    وقتی اسپرایت خوانده نشده باشد (fresh checkout ناقص)، چیزی مسدود نمی‌شود."""

    if not value:
        return
    names = available_icons()
    if not names:
        return
    if map_icon_name(value) not in names:
        raise ValidationError(
            "این نام آیکون در Lucide وجود ندارد. "
            "نام انگلیسی آیکون را از https://lucide.dev/icons انتخاب کنید."
        )


def icon_preview_html(name, *, size=22, color="#c9a15a", full=False):
    """اسنیپت یک آیکون Lucide — برای پیش‌نمایش در ادمین.

    رنگ پیش‌فرض طلاییِ پالت v2 است. ``full=True`` برای سازگاری با کد قدیمی
    نگه داشته شده و اثری ندارد."""

    if not name:
        return "—"
    name = map_icon_name(str(name))
    if not re.fullmatch(r"[a-z0-9-]+", name):
        return "—"
    return format_html(
        '<svg class="lucide" aria-hidden="true" focusable="false"'
        ' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
        ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
        ' width="{size}" height="{size}" style="color:{color}"'
        '><use href="{href}#{name}" /></svg>',
        size=size,
        color=color,
        href=sprite_url(),
        name=name,
    )


class IconPreviewMixin:
    """ستون «پیش‌نمایش آیکون» را برای مدل‌هایی با فیلد ``icon`` فراهم می‌کند."""

    @display(description="آیکون")
    def icon_preview(self, obj):
        return icon_preview_html(getattr(obj, "icon", "") or getattr(obj, "badge_icon", ""))


class IconPickerWidget(forms.TextInput):
    """پیکر آیکون: فیلد متنی + پیش‌نمایش زنده + یک جدولِ جستجوپذیر از همهٔ
    آیکون‌های اسپرایتِ Lucide (ادمین، بدون CDN). کلیدها کار می‌کنند: Escape
    می‌بندد، فلش‌ها جابه‌جا می‌شوند و Enter انتخاب می‌کند."""

    class Media:
        css = {
            "all": ["admin/css/icon_picker.css"],
        }
        js = [ADMIN_LIST_JS, "admin/js/icon_picker.js"]

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs.setdefault("data-ip-input", "")
        attrs.setdefault("data-ip-sprite", sprite_url())
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
        preview = icon_preview_html(value, size=20)
        return format_html(
            '<div class="icon-picker" data-icon-picker>'
            "<div class=\"ip-row\">{}"
            '<button type="button" class="ip-preview" data-ip-preview '
            'aria-label="انتخاب از میان آیکون‌ها" title="انتخاب آیکون">{}</button>'
            "</div>"
            '<p class="ip-error" data-ip-error hidden>چنین آیکونی در Lucide '
            "وجود ندارد. نام انگلیسی درست را از lucide.dev/icons پیدا کنید.</p>"
            '<div class="ip-popup" data-ip-popup hidden role="dialog" '
            'aria-label="انتخاب آیکون">'
            '<input type="search" class="ip-search" data-ip-search '
            'placeholder="جستجوی آیکون…" autocomplete="off" />'
            '<div class="ip-grid" data-ip-grid></div>'
            '<p class="ip-count" data-ip-count></p>'
            "</div>"
            "</div>",
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
