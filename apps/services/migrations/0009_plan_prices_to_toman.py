"""تبدیلِ قیمتِ پلن‌ها به تومان.

فیلدِ قیمتِ پلن قبلاً یک رشتهٔ آزاد بود (مثلاً «۱۵») و واحدِ آن — مثلِ
``ServiceCustomItem.price`` که هنوز هم «میلیون تومان» است — **میلیون تومان** بود.
حالا یک عددِ صحیحِ **تومان** است (مثلاً ۱۵۰۰۰۰۰۰). این migration یک‌بار
مقدارهای قدیمی را ضرب در یک‌میلیون می‌کند تا همانیِ واقعی حفظ شود:

    "15"  → 15 (توسطِ CAST در 0008) → ۱۵٬۰۰۰٬۰۰۰
    "از ۵۰" → 50 → ۵۰٬۰۰۰٬۰۰۰  (متنِ «از» دیگر نشان داده نمی‌شود؛ price_prefix
             این کار را برمی‌گردارد و پیش‌فرضش «از» است)

چون برعکس‌کردن به یک مقدارِ متنیِ از‌دست‌رفته برنمی‌گردد، no-op است (قیمت‌ها
عددیِشان را نگه می‌داریم — تبدیلِ برعکس بی‌معنی است).
"""

from django.db import migrations

FACTOR = 1_000_000


def convert_prices(apps, schema_editor):
    ServicePlan = apps.get_model("services", "ServicePlan")
    for plan in ServicePlan.objects.all():
        changed = False
        for field in ("price", "old_price"):
            value = getattr(plan, field)
            if value is None:
                continue
            # یک CAST ناموفق (مثلاً رشتهٔ غیرعددی) در SQLite به ۰ تبدیل می‌شود؛
            # ۰ یعنی «قیمتِ نامعتبر» → صدا زدنِ price_note به‌جای نشان‌دادنِ «۰».
            if value == 0:
                setattr(plan, field, None)
                changed = True
            elif value < 1000:
                # مقیاسِ قدیمی: میلیون تومان. مقادیری که از قبل به‌نظر می‌رسند
                # تومانِ کامل هستند (>= 1000) دست‌نخورده باقی می‌مانند.
                setattr(plan, field, value * FACTOR)
                changed = True
        if changed:
            plan.save(update_fields=["price", "old_price"])


def reverse(apps, schema_editor):
    """برعکس‌کردنِ مقیاس بی‌معنی است — عددِ تومان را نگه می‌داریم."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("services", "0008_service_accent_service_hero_cta_primary_text_and_more"),
    ]
    operations = [
        migrations.RunPython(convert_prices, reverse),
    ]
