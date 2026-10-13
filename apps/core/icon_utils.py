"""پشتیبانی آیکونِ Font Awesome (رایگان) برای ادمین و قالب‌ها.

کاملاً لوکال: اسکریپتِ ``scripts/build_fontawesome.js`` فونت وبِ پکیجِ
pinned شدهٔ ``@fortawesome/fontawesome-free`` را به ``static/fontawesome/``
کپی می‌کند و ``static/fontawesome/icons.json`` را می‌سازد — فهرستِ نامِ
آیکون‌های رایگان، دسته‌بندی‌شده بر اساس سبک (solid / regular / brands).
بدون CDN، و برخلافِ اسپرایتِ قدیمیِ Lucide هیچ چیز برای sync وجود ندارد:
فونت شاملِ همهٔ آیکون‌های رایگان است، پس هر چیزی که ادمین انتخاب کند
فوراً روی سایت نمایش داده می‌شود.

سبکِ پیش‌فرض solid است (تصمیمِ کاربر)؛ آیکون‌های برند (مثل linkedin)
خودکار با fa-brands رندر می‌شوند.
"""

import json
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

ICONS_REL_PATH = Path("fontawesome") / "icons.json"
FA_CSS_REL_PATH = "fontawesome/css/all.min.css"
DEFAULT_ICON = "wand-magic-sparkles"
DEFAULT_STYLE = "solid"

# نگاشتِ نام‌های قدیمیِ Lucide به نامِ معادل در Font Awesome. تمام نام‌های
# استفاده‌شده در قالب‌ها و دیتابیسِ فعلی را پوشش می‌دهد؛ اسکریپتِ بیلد این
# جدول را در برابر فهرستِ رسمی آیکون‌های رایگان اعتبارسنجی می‌کند.
LUCIDE_TO_FA = {
    # قالب‌ها
    "alert-circle": "circle-exclamation",
    "alert-triangle": "triangle-exclamation",
    "arrow-down": "arrow-down",
    "arrow-left": "arrow-left",
    "arrow-right": "arrow-right",
    "badge-check": "certificate",
    "book-open": "book-open",
    "briefcase": "briefcase",
    "calendar-days": "calendar-days",
    "check": "check",
    "chevron-down": "chevron-down",
    "chevron-left": "chevron-left",
    "chevron-right": "chevron-right",
    "clock": "clock",
    "external-link": "arrow-up-right-from-square",
    "globe": "globe",
    "layers": "layer-group",
    "link": "link",
    "linkedin": "linkedin-in",
    "mail": "envelope",
    "map-pin": "location-dot",
    "menu": "bars",
    "message-circle": "comment",
    "mic": "microphone",
    "move-horizontal": "left-right",
    "pause": "pause",
    "pen-tool": "pen-nib",
    "phone": "phone",
    "play": "play",
    "plus": "plus",
    "quote": "quote-right",
    "rocket": "rocket",
    "ruler": "ruler",
    "send": "paper-plane",
    "shield-check": "shield-halved",
    "shopping-cart": "cart-shopping",
    "smartphone": "mobile-screen-button",
    "sparkles": "wand-magic-sparkles",
    "star": "star",
    "user-round": "user",
    "users": "users",
    "x": "xmark",
    # دیتابیس
    "at-sign": "at",
    "award": "award",
    "box": "box",
    "boxes": "boxes-stacked",
    "braces": "code",
    "building-2": "building",
    "code-2": "code",
    "code-xml": "code",
    "component": "cube",
    "container": "box",
    "credit-card": "credit-card",
    "database": "database",
    "diamond": "gem",
    "figma": "figma",
    "file-text": "file-lines",
    "film": "film",
    "gauge": "gauge",
    "gem": "gem",
    "heart-handshake": "handshake-angle",
    "image": "image",
    "layout-dashboard": "table-columns",
    "layout-panel-top": "table-columns",
    "layout-template": "table",
    "megaphone": "bullhorn",
    "monitor-smartphone": "mobile-screen",
    "newspaper": "newspaper",
    "orbit": "circle-nodes",
    "palette": "palette",
    "party-popper": "cake-candles",
    "printer": "newspaper",
    "refresh-cw": "arrows-rotate",
    "search": "magnifying-glass",
    "shapes": "shapes",
    "smile": "face-smile",
    "square-code": "code",
    "square-terminal": "terminal",
    "store": "store",
    "terminal": "terminal",
    "trending-up": "arrow-trend-up",
    "type": "font",
    "webhook": "plug",
    "workflow": "diagram-project",
    "zap": "bolt",
}


@lru_cache(maxsize=1)
def _load_icons():
    """دیکشنریِ {style: [names]} از icons.json، یا {} اگر هنوز بیلد نشده."""
    for base in settings.STATICFILES_DIRS:
        candidate = Path(base) / ICONS_REL_PATH
        if candidate.is_file():
            try:
                return json.loads(candidate.read_text(encoding="utf-8")).get("styles", {})
            except (OSError, ValueError):
                pass
    return {}


@lru_cache(maxsize=2)
def available_icons(full=False):
    """frozenset از همهٔ نام‌های آیکون‌های رایگان Font Awesome (همهٔ سبک‌ها).

    آرگومان ``full`` برای سازگاری با کد قدیمی نگه داشته شده و دیگر معنایی
    ندارد — فونت شاملِ همهٔ آیکون‌هاست و نیازی به sync نیست."""

    styles = _load_icons()
    out = set()
    for names in styles.values():
        out.update(names)
    return frozenset(out)


def icon_style(name):
    """سبکِ رندر: 'brands' برای آیکون‌های برند، در غیر این صورت 'solid'."""
    if name in _load_icons().get("brands", ()):
        return "brands"
    return DEFAULT_STYLE


def map_icon_name(name):
    """تبدیل یک نام قدیمیِ Lucide به معادلِ Font Awesome آن."""
    return LUCIDE_TO_FA.get(name, name)


def validate_icon_name(value):
    """ولیدیتورِ فیلدِ آیکون — مقدار باید یک نام واقعی در Font Awesome رایگان باشد.

    وقتی icons.json هنوز ساخته نشده (fresh checkout بدون بیلد)، چیزی مسدود
    نمی‌شود."""

    if not value:
        return
    names = available_icons()
    if not names:
        return
    if value not in names:
        raise ValidationError(
            "این نام آیکون در Font Awesome (نسخهٔ رایگان) وجود ندارد. "
            "نام انگلیسی آیکون را از https://fontawesome.com/icons انتخاب کنید."
        )


def icon_preview_html(name, *, size=22, color="#c9a15a", full=False):
    """اسنیپت یک آیکون Font Awesome — برای پیش‌نمایش در ادمین.

    رنگ پیش‌فرض طلاییِ پالت v2 است. ``full=True`` برای سازگاری با کد قدیمی
    نگه داشته شده و اثری ندارد (فونت همهٔ آیکون‌ها را دارد)."""

    if not name:
        return "—"
    name = map_icon_name(name)
    style = icon_style(name)
    return format_html(
        '<i class="fa-{} fa-{}" aria-hidden="true" '
        'style="font-size:{}px;line-height:1;color:{}"></i>',
        style,
        name,
        size,
        color,
    )


class IconPreviewMixin:
    """ستون «پیش‌نمایش آیکون» را برای مدل‌هایی با فیلد ``icon`` فراهم می‌کند."""

    @display(description="آیکون")
    def icon_preview(self, obj):
        return icon_preview_html(getattr(obj, "icon", "") or getattr(obj, "badge_icon", ""))


class IconPickerWidget(forms.TextInput):
    """پیکر آیکون: فیلد متنی + پیش‌نمایش زنده + یک جدولِ جستجوپذیر از همهٔ
    آیکون‌های رایگان Font Awesome (فقط ادمین، بدون CDN). کلیدها کار می‌کنند:
    Escape می‌بندد، فلش‌ها جابه‌جا می‌شوند و Enter انتخاب می‌کند."""

    class Media:
        css = {
            "all": [FA_CSS_REL_PATH, "admin/css/icon_picker.css"],
        }
        js = ["admin/js/fa_icons.js", "admin/js/icon_picker.js"]

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
        preview = icon_preview_html(value, size=20)
        return format_html(
            '<div class="icon-picker" data-icon-picker>'
            "<div class=\"ip-row\">{}"
            '<button type="button" class="ip-preview" data-ip-preview '
            'aria-label="انتخاب از میان آیکون‌ها" title="انتخاب آیکون">{}</button>'
            "</div>"
            '<p class="ip-error" data-ip-error hidden>چنین آیکونی در Font Awesome '
            "وجود ندارد. نام انگلیسی درست را از fontawesome.com/icons پیدا کنید.</p>"
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
