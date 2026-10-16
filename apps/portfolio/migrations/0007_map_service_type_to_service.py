"""نگاشتِ best-effortِ فیلدِ متنیِ «حوزه کاری» به ارتباطِ واقعیِ خدمت.

`Portfolio.service_type` یک فیلدِ متنیِ آزاد است و می‌تواند هر چیزی باشد
(مثلاً «فروش عطر و ادکلن»)؛ به همین دلیل به‌جای جایگزینی، یک FK اختیاریِ
`service` اضافه شد که کاروسلِ «پروژه‌های این خدمت» از آن استفاده می‌کند و
فیلدِ متنی به‌عنوانِ fallback سرِ جایش می‌ماند (هرگز حذف نمی‌شود).

این migration یک‌بار و به‌صورتِ best-effort برای پروژه‌هایی که هنوز خدمتِ
مرتبط ندارند اجرا می‌شود: اول تطابقِ دقیقِ عنوان، سپس تطابقِ بدونِ نیم‌فاصله
(«برنامه‌نویسی» در برابر «برنامه نویسی»). تطابقی پیدا نشد → پروژه دست‌نخورده
می‌ماند (FK خالی، همان fallbackِ متنی).
"""

import re

from django.db import migrations


def normalize(text):
    """حذفِ فاصله/نیم‌فاصله و نرمال‌سازیِ «ی»/«ک» برای تطابقِ سست‌تر."""
    if not text:
        return ""
    t = str(text).strip()
    t = t.replace("‌", "").replace("‌", "")  # ZWNJ
    t = re.sub(r"\s+", " ", t)
    t = t.replace("ي", "ی").replace("ك", "ک")
    return t.lower()


def map_service_types(apps, schema_editor):
    Portfolio = apps.get_model("portfolio", "Portfolio")
    Service = apps.get_model("services", "Service")
    by_norm = {normalize(s.title): s for s in Service.objects.all()}
    if not by_norm:
        return
    for project in Portfolio.objects.filter(service__isnull=True):
        norm = normalize(project.service_type)
        if not norm:
            continue
        # تطابقِ دقیق، بعد تطابقِ جزیی که عنوانِ خدمت در حوزهٔ کاری باشد
        # (مثلاً «طراحی سایت فروشگاهی» شاملِ «طراحی سایت»).
        match = by_norm.get(norm)
        if match is None:
            for key, service in by_norm.items():
                if key and (key in norm or norm in key):
                    match = service
                    break
        if match is not None:
            project.service = match
            project.save(update_fields=["service"])


def reverse(apps, schema_editor):
    """برعکس: ارتباط‌هایی که این migration ساخته را پاک می‌کند، ولی فیلدِ متنی
    که از قبل هم بوده دست‌نخورده می‌ماند."""
    Portfolio = apps.get_model("portfolio", "Portfolio")
    Portfolio.objects.all().update(service=None)


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0006_portfolio_service"),
    ]
    operations = [
        migrations.RunPython(map_service_types, reverse),
    ]
