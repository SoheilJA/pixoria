"""Rebuild the public Lucide sprite from the database + template usages.

Run after picking new icons in the admin::

    python manage.py sync_icons

It collects every icon value stored in all model icon fields (any field
validated by ``validate_icon_name``), passes them to
``node scripts/build_icon_sprite.js --extra <tmpfile>`` together with the
template ``{% icon "…" %}`` usages the script scans itself, and rebuilds:

* ``static/icons/lucide.sprite.svg`` — the small public sprite;
* ``static/icons/lucide.full.sprite.svg`` — the admin-only full sprite;
* ``static/admin/js/lucide_full_icons.js`` — the picker name lists.

Idempotent: running it twice with the same DB and templates produces the same
output.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.icon_utils import validate_icon_name

BASE_DIR = settings.BASE_DIR
BUILD_SCRIPT = BASE_DIR / "scripts" / "build_icon_sprite.js"


class Command(BaseCommand):
    help = "اسپرایت آیکون‌های Lucide را از دیتابیس و قالب‌ها بازسازی می‌کند."

    def handle(self, *args, **options):
        # کنسول ویندوز cp1252 است — پیام‌های فارگی روی آن شکست می‌خورند (D21)
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass

        names = self.collect_db_icons()
        self.stdout.write(f"آیکون‌های دیتابیس: {len(names)}")

        node = shutil.which("node") or "node"
        extra = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False, encoding="utf-8"
            ) as tmp:
                json.dump(sorted(names), tmp)
                extra = tmp.name
            result = subprocess.run(
                [node, str(BUILD_SCRIPT), "--extra", extra],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        finally:
            if extra and os.path.exists(extra):
                os.unlink(extra)

        if result.returncode != 0:
            self.stderr.write(
                "ساخت اسپرایت شکست خورد:\n" + (result.stderr or result.stdout)
            )
            raise SystemExit(1)
        self.stdout.write(result.stdout.strip())

    def collect_db_icons(self):
        """مقادیرِ همهٔ فیلدهای آیکون (هر فیلدی با اعتبارسنج validate_icon_name)."""
        names = set()
        for model in apps.get_models():
            for field in model._meta.get_fields():
                validators = getattr(field, "validators", None) or []
                if not any(v is validate_icon_name for v in validators):
                    continue
                if not getattr(field, "concrete", False):
                    continue
                values = (
                    model.objects.values_list(field.name, flat=True)
                    .exclude(**{f"{field.name}__isnull": True})
                    .distinct()
                )
                for value in values:
                    if value:
                        names.add(value.strip())
        return names
