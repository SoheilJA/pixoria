"""پشتیبانی آیکونِ Tabler Icons (وبفونتِ outline) برای ادمین و قالب‌ها.

کاملاً لوکال: وبفونت در ``static/tabler/`` به صورت شناور است
(``tabler-icons.min.css`` + ``fonts/tabler-icons.woff2``؛ Tabler ۳.۴۹).
فهرستِ نام‌ها هنگامِ اجرا از خودِ CSS خوانده می‌شود — پس هر چیزی که ادمین
انتخاب کند فوراً روی سایت نمایش داده می‌شود و برای سینک چیزی لازم نیست.
اسکریپتِ ``scripts/build_tabler_icons.py`` فقط لیستِ جاوااسکریپتِ ادمین
(``static/admin/js/tabler_icons.js``) را از همان CSS تولید می‌کند.

تمامِ آیکون‌ها سبکِ outline فونتِ ``tabler-icons`` هستند و آیکون‌های برند
(مثل brand-instagram) هم داخلِ همین فونت‌اند — پس نکتهٔ سبک/فامیلی دیگر
وجود ندارد. کلاسِ رندر: ``ti ti-<name>``.
"""

import re
from functools import lru_cache
from pathlib import Path

from django import forms
from django.conf import settings
from django.contrib.admin import display
from django.core.exceptions import ValidationError
from django.forms.widgets import flatatt
from django.utils.html import format_html
from django.utils.safestring import mark_safe

TABLER_CSS_REL_PATH = "tabler/tabler-icons.min.css"
ADMIN_LIST_JS = "admin/js/tabler_icons.js"
DEFAULT_ICON = "sparkles"
_CLASS_RE = re.compile(r"\.ti-([a-z0-9-]+):before")

# نام‌های قدیمیِ DB (سبکِ Lucide/Font Awesome) به معادلِ Tabler. نام‌هایی
# که عیناً در Tabler موجودند (مثل arrow-left، palette، zap→bolt استثنا
# نیست چون map قبل از اعتبارسنجی اجرا می‌شود) نیازی به ورود نداشته و
# خودکار عبور می‌کنند؛ این جدول فقط پرش‌ها را پوشش می‌دهد و
# scripts/build_tabler_icons.py وجودِ مقصدها را در برابر فونت اعتبارسنجی می‌کند.
LEGACY_ALIASES = {
    # قالب‌ها
    "at-sign": "at",
    "badge-check": "rosette-discount-check",
    "book-open": "book",
    "boxes": "box-multiple",
    "building-2": "buildings",
    "calendar-days": "calendar",
    "comment": "message-circle",
    "code-2": "code",
    "code-xml": "code",
    "component": "components",
    "figma": "brand-figma",
    "film": "movie",
    "gem": "diamond",
    "layers": "stack-2",
    "layout-panel-top": "layout-sidebar",
    "layout-template": "template",
    "linkedin": "brand-linkedin",
    "instagram": "brand-instagram",
    "github": "brand-github",
    "telegram": "brand-telegram",
    "twitter": "brand-twitter",
    "x-twitter": "brand-x",
    "whatsapp": "brand-whatsapp",
    "youtube": "brand-youtube",
    "facebook": "brand-facebook",
    "dribbble": "brand-dribbble",
    "behance": "brand-behance",
    "megaphone": "speakerphone",
    "mic": "microphone",
    "monitor-smartphone": "devices-2",
    "move-horizontal": "arrows-horizontal",
    "newspaper": "news",
    "party-popper": "confetti",
    "pause": "player-pause",
    "pen-tool": "pencil",
    "refresh-cw": "refresh",
    "smile": "mood-smile",
    "square-code": "source-code",
    "square-terminal": "terminal-2",
    "shapes": "shape-3",
    "smartphone": "device-mobile",
    "store": "building-store",
    "table-cells-large": "table",
    "type": "typography",
    "user-round": "user",
    "wand-magic-sparkles": "sparkles",
    "workflow": "sitemap",
    "zap": "bolt",
}


@lru_cache(maxsize=1)
def available_icons(full=False):
    """frozenset از نام‌های آیکون‌های فونتِ محلیِ Tabler.

    فرمت ``full`` برای سازگاری با کدِ قدیمیِ نگه داشته شده و اثری ندارد.

    وقتی CSS هنوز در دسترس نباشد (فایل جدید اصطلاحاً «فرسوده» — ولی
    ``git checkout`` استاندارد شاملِ فونت است)، خروجی خالی است و پس ولیدینگ
    و رندر هیچ چیز مسدود نمی‌شوند (fail-soft)."""

    for base in settings.STATICFILES_DIRS:
        candidate = Path(base) / TABLER_CSS_REL_PATH
        if candidate.is_file():
            try:
                css = candidate.read_text(encoding="utf-8")
                return frozenset(_CLASS_RE.findall(css))
            except (OSError, UnicodeDecodeError):
                pass
    return frozenset()


def map_icon_name(name):
    """تبدیل یک نامِ قدیمی (سبکِ Lucide) به معادلِ Tabler آن."""
    return LEGACY_ALIASES.get(str(name), str(name))


def validate_icon_name(value):
    """ولیدیتورِ فیلدِ آیکون — بعد از نگاشت باید در فونتِ محلی موجود باشد.

    وقتی CSS خوانده نشده باشد (fresh checkout ناقص)، چیزی مسدود نمی‌شود."""

    if not value:
        return
    names = available_icons()
    if not names:
        return
    if map_icon_name(value) not in names:
        raise ValidationError(
            "این نام آیکون در Tabler Icons وجود ندارد. "
            "نام انگلیسی آیکون را از https://tabler.io/icons انتخاب کنید."
        )


def icon_preview_html(name, *, size=22, color="#c9a15a", full=False):
    """اسنیپت یک آیکون Tabler — برای پیش‌نمایش در ادمین.

    رنگ پیش‌فرض طلاییِ پالت v2 است. ``full=True`` برای سازگاری با کد قدیمی
    نگه داشته شده و اثری ندارد."""

    if not name:
        return "—"
    name = map_icon_name(name)
    return format_html(
        '<i class="ti ti-{}" aria-hidden="true" '
        'style="font-size:{}px;line-height:1;color:{}"></i>',
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
    آیکون‌های فونتِ Tabler (ادمین، بدون CDN). کلیدها کار می‌کنند: Escape
    می‌بندد، فلش‌ها جابه‌جا می‌شوند و Enter انتخاب می‌کند."""

    class Media:
        css = {
            "all": [TABLER_CSS_REL_PATH, "admin/css/icon_picker.css"],
        }
        js = [ADMIN_LIST_JS, "admin/js/icon_picker.js"]

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
            '<p class="ip-error" data-ip-error hidden>چنین آیکونی در Tabler '
            "وجود ندارد. نام انگلیسی درست را از tabler.io/icons پیدا کنید.</p>"
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
