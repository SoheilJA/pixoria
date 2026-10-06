"""پر کردن محتوای پیش‌فرض صفحهٔ آرشیو نمونه‌کارها با متن فارسیِ طرح v2.

بعد از migrate اجرا شود:

    python manage.py seed_portfolio_content

Idempotent: عنوان و توضیحاتِ هیروسکشن اگر از قبل وجود داشته باشند
دست‌نخورده باقی می‌مانند (قانون «محتوای ویرایش‌شده در ادمین هرگز بازنویسی
نمی‌شود» — فقط فیلدهای خالی پر می‌شوند). دادهٔ خود پروژه‌ها (آمار، گالری،
تکنولوژی‌ها) کاملاً دستی است و این دستور به آن‌ها دست نمی‌زند، چون نمونه‌کارها
پروژه‌های واقعیِ کاربر هستند."""
import sys

from django.core.management.base import BaseCommand

from apps.portfolio.models import Category, Portfolio, PortfolioPageSection


# هیروی آرشیو نمونه‌کارها. عنوان/توضیحات از دیتابیس نگه داشته می‌شوند؛
# فقط eyebrow (فیلد جدید) وقتی خالی باشد پر می‌شود.
EYEBROW = "نمونه‌کارها"

# دسته‌بندی‌های پیش‌فرض آرشیو — فقط وقتی هیچ دسته‌ای وجود ندارد ساخته می‌شوند
# تا فیلترِ صفحهٔ آرشیو روی یک دیتابیسِ خالی هم کار کند. اسلاگ‌ها با
# `Category.filter_url` (؟category=slug) همخوانی دارند.
DEFAULT_CATEGORIES = [
    {"name": "طراحی سایت", "slug": "web-design"},
    {"name": "برنامه‌نویسی", "slug": "programming"},
    {"name": "طراحی گرافیک", "slug": "graphic-design"},
    {"name": "طراحی لوگو", "slug": "logo-design"},
]


class Command(BaseCommand):
    help = "پر کردن محتوای پیش‌فرض صفحهٔ آرشیو نمونه‌کارها با متن فارسیِ طرح v2"

    def handle(self, *args, **options):
        # کنسول ویندوز به‌طور پیش‌فرض cp1252 است و روی پیام‌های فارسی خطا می‌دهد.
        sys.stdout.reconfigure(encoding="utf-8")

        self.seed_hero()
        self.seed_categories()

    def seed_hero(self):
        section = PortfolioPageSection.objects.first()
        if section is None:
            # دیتابیس خالی — یک سکشنِ حداقلی می‌سازد تا ویو بدون گارد کار کند.
            section = PortfolioPageSection.objects.create(
                eyebrow=EYEBROW,
                title="نمونه‌کارهای پیکسوریا",
                description=(
                    "مجموعه‌ای از پروژه‌هایی که با دقت، اشتیاق و توجه به جزئیات "
                    "ساخته‌ایم."
                ),
            )
            self.stdout.write("هیروسکشن آرشیو: ساخته شد")
            return

        if section.eyebrow:
            self.stdout.write(
                f"هیروسکشن آرشیو: از قبل موجود — دست‌نخورده ({section})"
            )
            return

        section.eyebrow = EYEBROW
        section.save(update_fields=["eyebrow"])
        self.stdout.write(f"هیروسکشن آرشیو: eyebrow پر شد ({section})")

    def seed_categories(self):
        if Category.objects.exists():
            self.stdout.write(
                f"دسته‌بندی‌ها: {Category.objects.count()} ردیف از قبل موجود — دست‌نخورده"
            )
            return

        for order, fields in enumerate(DEFAULT_CATEGORIES):
            Category.objects.create(order=order, **fields)
        self.stdout.write(
            f"دسته‌بندی‌ها: {Category.objects.count()} ردیف پیش‌فرض ساخته شد"
        )

        if Portfolio.objects.exists():
            self.stdout.write(
                "نکته: نمونه‌کارهای موجود دست‌نخورده باقی ماندند — "
                "دسته‌بندیِ آن‌ها را در ادمین ویرایش کنید."
            )
