import django.db.models.deletion
from django.db import migrations, models


def remove_contact_section(apps, schema_editor):
    """سطرِ بخش «فرم تماس سریع» حذف می‌شود تا صفحه اصلی دیگر پارشال
    _contact.html را رندر نکند. برگشتِ مهاجرت ممکن نیست چون خود مدل‌ها در
    همین مهاجرت حذف می‌شوند، بنابراین noop است."""

    HomeSection = apps.get_model("home", "HomeSection")
    HomeSection.objects.filter(key="contact").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0010_rename_home_section_keys"),
        ("services", "0006_service_badge_service_card_span_service_chips_and_more"),
    ]

    operations = [
        # ابتدا سطرِ HomeSection مربوط به کلید contact (پارشالش دیگر وجود
        # ندارد و در غیر این صورت رندر صفحه اصلی خطای TemplateDoesNotExist
        # می‌داد).
        migrations.RunPython(remove_contact_section, migrations.RunPython.noop),
        # کلید contact از KEY_CHOICES حذف می‌شود تا دیگر در پنل ادمین قابل
        # انتخاب نباشد.
        migrations.AlterField(
            model_name="homesection",
            name="key",
            field=models.CharField(
                choices=[
                    ("hero", "هیرو"),
                    ("about", "درباره ما"),
                    ("services", "خدمات"),
                    ("trusted", "برندهای همکار"),
                    ("portfolio", "نمونه‌کارها"),
                    ("why", "چرا پیکسوریا"),
                    ("process", "فرآیند کار"),
                    ("testimonials", "نظرات مشتریان"),
                    ("tech", "تکنولوژی‌ها و مهارت‌ها"),
                    ("stats", "آمار و ارقام"),
                    ("blog", "آخرین مقالات"),
                    ("faq", "سوالات متداول"),
                ],
                max_length=30,
                unique=True,
                verbose_name="کلید بخش",
            ),
        ),
        # سپس مدل‌ها. هیچ مدل دیگری به آن‌ها FK ندارد؛ HomeLead خودش به
        # services.Service وابسته بود که با حذف این مدل از بین می‌رود.
        migrations.DeleteModel(name="ContactSection"),
        migrations.DeleteModel(name="HomeLead"),
    ]
