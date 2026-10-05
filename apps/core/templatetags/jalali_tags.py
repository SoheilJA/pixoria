"""Gregorian → Jalali (شمسی) date filter for Persian front-end dates.

Usage:  {{ article.published_at|fa_jdate }}   →  ۱۲ آبان ۱۴۰۳

The v2 blog cards show Jalali dates and Django has no built-in Jalali support,
so the conversion comes from jdatetime (pure Python, no C extension).
"""

from datetime import date, datetime

import jdatetime
from django import template

register = template.Library()

_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


@register.filter
def fa_jdate(value):
    """تاریخ میلادی → «۱۲ آبان ۱۴۰۳». None و مقادیر نامعتبر خالی برمی‌گردند."""
    if isinstance(value, datetime):
        value = value.date()
    if not isinstance(value, date):
        return ""
    jalali = jdatetime.date.fromgregorian(date=value)
    return jalali.strftime("%-d %B %Y").translate(_DIGITS)
