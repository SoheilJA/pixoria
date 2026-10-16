from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0013_delete_heromarqueeitem_delete_manifestosection_and_more"),
    ]

    operations = [
        migrations.DeleteModel(name="NavItem"),
    ]
