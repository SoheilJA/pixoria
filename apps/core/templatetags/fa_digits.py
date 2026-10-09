"""Persian digit filter.

Usage:  {{ value|fa_digits }}        →  ۰۹۱۲۳۴۵۶۷۸
        {{ forloop.counter|stringformat:"02d"|fa_digits }}  →  ۰۱
        {{ seconds|fa_duration }}   →  ۰:۴۸  (mm:ss for media cards)

Converts latin digits to Persian ones so ordinals, counters and phone numbers
render in fa-IR. Values that already use Persian digits pass through untouched,
and non-numeric text is left as-is (only digit runs are translated).
"""

from django import template

register = template.Library()

_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


@register.filter
def fa_digits(value):
    if value is None:
        return ""
    return str(value).translate(_DIGITS)


@register.filter
def fa_duration(seconds):
    """ثانیه → زمان فارسی برای کارت‌های ویدیو/صوت اسلایدر نظرات.

    48 → "۰:۴۸"، 65 → "۱:۰۵"
    """
    try:
        total = int(float(seconds))
    except (TypeError, ValueError):
        return ""
    minutes, rest = divmod(total, 60)
    return f"{minutes}:{rest:02d}".translate(_DIGITS)


@register.filter
def fa_price(value):
    """قیمت (عدد) → فارسی با جداکنندهٔ هزارگان.

    15000000 → "۱۵٬۰۰۰٬۰۰۰" (با U+066C، جداسازِ هزارگانِ فارسی).
    برای قیمت‌های پلن‌ها استفاده می‌شود؛ مقدارِ غیرعددی خالی برمی‌گردد.
    """
    try:
        amount = int(value)
    except (TypeError, ValueError):
        return ""
    return f"{amount:,}".replace(",", "٬").translate(_DIGITS)
