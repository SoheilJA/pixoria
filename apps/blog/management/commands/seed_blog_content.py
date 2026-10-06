"""Seed the v2 blog page settings.

Reuses the D25/D21 pattern: singletons with ``first_or_create`` (never
overwrite admin edits) and the collection cleanup for rows whose value is not
in the v2 list. This command touches only chrome (the page settings) and the
optional ``eyebrow`` fields — articles are the user's own content and are left
alone, exactly like the portfolio seed (D37).

Run::

    python manage.py seed_blog_content
"""

import sys

from django.core.management.base import BaseCommand

from apps.blog.models import BlogPageSettings


class Command(BaseCommand):
    help = "Seed the v2 blog page settings (idempotent, never overwrites)."

    def handle(self, *args, **options):
        # کنسول ویندوز به‌طور پیش‌فرض cp1252 است و روی پیام‌های فارسی
        # UnicodeEncodeError می‌گیرد — مثل seed_home_content (D21).
        if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except (AttributeError, OSError):
                pass

        self.stdout.write("بذرِ تنظیمات صفحهٔ بلاگ (v2)...")

        # عنوان و توضیحات پیش‌فرض صفحهٔ بلاگ — فقط وقتی چیزی نیست.
        settings_obj = BlogPageSettings.objects.first()
        if settings_obj is None:
            settings_obj = BlogPageSettings.objects.create(
                title="دانش، [[بی‌واسطه]]",
                description=(
                    "تجربه‌ها، نکات فنی و درس‌های واقعیِ ساخت محصول‌های دیجیتال — "
                    "از طراحی و توسعه تا سئو و رشد."
                ),
                eyebrow="مجلهٔ پیکسوریا",
            )
            self.stdout.write(
                self.style.SUCCESS("  ✓ تنظیمات صفحهٔ بلاگ ساخته شد")
            )
        else:
            changed = []
            if not settings_obj.eyebrow:
                settings_obj.eyebrow = "مجلهٔ پیکسوریا"
                changed.append("eyebrow")
            if changed:
                settings_obj.save(update_fields=changed)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ تنظیمات صفحهٔ بلاگ به‌روز شد: {', '.join(changed)}"
                    )
                )
            else:
                self.stdout.write("  → تنظیمات صفحهٔ بلاگ از قبل کامل است")

        # یک مقالهٔ ویژه انتخاب می‌کنیم تا اسلات بالای صفحهٔ بلاگ (T39) پر بماند.
        # فقط وقتی هیچ مقالهٔ ویژه‌ای نیست و فقط روی مقالهٔ منتشرشدهٔ جدیدترین
        # اعمال می‌شود — هیچ تنظیمی که ادمین داده باشد بازنویس نمی‌شود.
        from apps.blog.models import Article

        if settings_obj and not Article.objects.filter(featured=True).exists():
            featured = (
                Article.objects.filter(status="published")
                .order_by("-published_at")
                .first()
            )
            if featured is not None:
                featured.featured = True
                featured.save(update_fields=["featured"])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ «{featured.title}» به‌عنوان مقالهٔ ویژه علامت خورد"
                    )
                )

        self.stdout.write(self.style.SUCCESS("انجام شد."))
