# تغییر کلیدهای بخش‌های صفحه اصلی به کلیدهای v2 و حذف ردیف‌های سکشن‌هایی که
# در طرح جدید پارشال ندارند (مانیفست). پارشال‌های قدیمی مثل _clients.html با
# _trusted.html جایگزین می‌شوند، پس کلید ردیف‌های موجود هم باید هم‌خوان شود.

from django.db import migrations

# کلید قدیمی → کلید جدید (پارشال جدید)
KEY_RENAMES = {
    "clients": "trusted",
    "works": "portfolio",
    "articles": "blog",
}

# سکشن‌هایی که در طرح v2 حذف شده‌اند و پارشالشان وجود ندارد.
DROPPED_KEYS = ["manifesto"]


def rename_keys(apps, schema_editor):
    HomeSection = apps.get_model("home", "HomeSection")
    for old_key, new_key in KEY_RENAMES.items():
        HomeSection.objects.filter(key=old_key).update(key=new_key)
    HomeSection.objects.filter(key__in=DROPPED_KEYS).delete()


def restore_keys(apps, schema_editor):
    HomeSection = apps.get_model("home", "HomeSection")
    for old_key, new_key in KEY_RENAMES.items():
        HomeSection.objects.filter(key=new_key).update(key=old_key)


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0009_homeaboutsection_testimonialsection_trustedsection_and_more"),
    ]

    operations = [
        migrations.RunPython(rename_keys, restore_keys),
    ]
