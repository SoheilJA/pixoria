"""تبدیلِ تصاویرِ موجود به WebPِ فشرده.

تصاویری که قبل از فعال‌شدنِ فشرده‌سازیِ خودکار (در saveِ مدل‌ها) آپلود
شده‌اند هنوز JPEG/PNG هستند. این کامند آن‌ها را با همان تابعی که موقعِ
آپلود استفاده می‌شود دوباره ذخیره می‌کند تا همهٔ تصاویر سایت یکدست شوند.

    python manage.py compress_images              ← فقط گزارش می‌دهد
    python manage.py compress_images --write      ← واقعاً تبدیل می‌کند

Idempotent: تصاویری که از قبل WebP هستند نادیده گرفته می‌شوند.
"""

from django.apps import apps
from django.core.management.base import BaseCommand

from apps.core.image_utils import compress_to_webp_if_smaller

# فیلدهای تصویری که باید بررسی شوند — app/model/field. باید با
# WEBP_FIELDSِ هر مدل (در image_utils.py) هماهنگ باشد.
FIELDS = [
    ("portfolio", "Portfolio", "image"),
    ("portfolio", "ProjectImage", "image"),
    ("blog", "Author", "avatar"),
    ("blog", "Article", "cover_image"),
    ("services", "Service", "og_image"),
    ("services", "ServiceSection", "image"),
    ("services", "ServiceTestimonial", "author_image"),
    ("services", "ServiceTestimonial", "video_poster"),
    ("core", "AboutStory", "image"),
]


def human(num):
    """اندازهٔ فایل را به شکلِ خوانا برمی‌گرداند."""
    for unit in ("B", "KB", "MB"):
        if num < 1024:
            return f"{num:.0f} {unit}"
        num /= 1024
    return f"{num:.1f} GB"


class Command(BaseCommand):
    help = "تصاویر نمونه‌کارهای موجود را به WebPِ فشرده تبدیل می‌کند."

    def add_arguments(self, parser):
        parser.add_argument(
            "--write",
            action="store_true",
            help="در غیر این حالت فقط گزارش می‌دهد و فایلی را تغییر نمی‌دهد.",
        )

    def handle(self, *args, **options):
        dry = not options["write"]
        self.stdout.write(
            self.style.WARNING("حالت خشک (dry-run) — چیزی نوشته نمی‌شود.")
            if dry else "حالتِ نوشتن."
        )

        converted, skipped, failed, grown = [], [], [], []
        for app_label, model_name, field_name in FIELDS:
            model = apps.get_model(app_label, model_name)
            for obj in model.objects.all():
                field = getattr(obj, field_name)
                if not field.name:
                    continue
                if field.name.endswith(".webp"):
                    skipped.append(field.name)
                    continue
                try:
                    old_name, old_size = field.name, field.size
                    source = field.file
                    compressed = compress_to_webp_if_smaller(source)
                    # اگر فشرده‌سازی حجم را بیشتر کرد (مثلاً JPEGِ بسیار فشردهٔ
                    # قبلی) تبدیل بی‌فایده است و فقط کیفیت را کم می‌کند.
                    if compressed is None:
                        grown.append((old_name, old_size))
                        continue
                    # PIL فایلِ مبدا را باز نگه می‌دارد؛ در ویندوز تا بسته
                    # نشود نمی‌توان آن را حذف کرد.
                    try:
                        source.close()
                    except Exception:  # noqa: BLE001
                        pass

                    if dry:
                        # در حالتِ خشک هیچ فایلی نوشته نمی‌شود —
                        # FieldFile.save(save=False) نیز فایل را روی دیسک
                        # می‌نویسد و فقط ذخیرهٔ مدل را رد می‌کند.
                        converted.append(
                            (old_name, field.storage.get_available_name(compressed.name),
                             old_size, compressed.size)
                        )
                        continue

                    # نامِ فایل از ContentFileِ بازگشتی خوانده می‌شود — نه از
                    # نامِ قدیمی؛ وگرنه محتوای WebP با پسوندِ jpg ذخیره می‌شد.
                    field.save(compressed.name, compressed, save=False)
                    obj.save(update_fields=[field_name])
                    new_field = getattr(obj, field_name)
                    converted.append((old_name, new_field.name, old_size, new_field.size))
                    # فایلِ قدیمی دیگر ارجاعی ندارد؛ حذف می‌شود.
                    try:
                        if field.storage.exists(old_name):
                            field.storage.delete(old_name)
                    except Exception:  # noqa: BLE001
                        self.stdout.write(
                            self.style.WARNING(f"  فایلِ قدیمی حذف نشد: {old_name}")
                        )
                except Exception as exc:  # noqa: BLE001
                    failed.append((field.name, str(exc)))

        for old, new, o_size, n_size in converted:
            saving = round((1 - n_size / o_size) * 100, 1) if o_size else 0
            self.stdout.write(
                self.style.SUCCESS(
                    f"  تبدیل شد: {old} → {new}  "
                    f"{human(o_size)} → {human(n_size)} ({saving}% کوچک‌تر)"
                )
            )
        for name in skipped:
            self.stdout.write(f"  از قبل WebP: {name}")
        for name, o_size in grown:
            self.stdout.write(
                f"  رد شد (WebP بزرگ‌تر می‌شد): {name}  {human(o_size)}"
            )
        for name, exc in failed:
            self.stdout.write(self.style.ERROR(f"  خطا: {name} — {exc}"))

        self.stdout.write(
            f"\nجمع: {len(converted)} تبدیل، {len(skipped)} WebPِ موجود، "
            f"{len(grown)} ردشده، {len(failed)} خطا."
        )
        if dry and converted:
            self.stdout.write(
                self.style.WARNING(
                    "برای اعمالِ واقعی دوباره با --write اجرا کنید."
                )
            )
