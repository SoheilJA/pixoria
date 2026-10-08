"""Fix the typo in the web-design category name («طراحی سیات» → «طراحی سایت»).

The slug (`web-design`) was already correct and is left untouched, so no URLs
change. The migration is idempotent: it only rewrites rows that still contain
the typo, so re-applying it (or applying it to an already-fixed DB) is a no-op.
"""

from django.db import migrations


def fix_typo(apps, schema_editor):
    Category = apps.get_model("portfolio", "Category")
    Category.objects.filter(name="طراحی سیات").update(name="طراحی سایت")


def reverse_typo(apps, schema_editor):
    # Reversing would re-introduce a typo on purpose; there is no sane reverse.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0004_portfolio_image_alt_portfolio_meta_description_and_more"),
    ]

    operations = [
        migrations.RunPython(fix_typo, reverse_typo),
    ]
