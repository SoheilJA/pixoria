"""پر کردن محتوای پیش‌فرض صفحهٔ «درباره ما» با متن فارسیِ طرح v2.

متن‌ها از `new/about.html` گرفته شده‌اند. بعد از migrate اجرا شود:

    python manage.py seed_about_content

Idempotent: سینگلتون‌هایی که از قبل وجود داشته باشند دست‌نخورده باقی می‌مانند
(قانون «محتوای ویرایش‌شده در ادمین هرگز بازنویسی نمی‌شود»). تنها استثنا مجموعهٔ
آمار است: ردیف‌های قدیمیِ v1 که در فهرست v2 نیستند حذف می‌شوند، درست مثل پاکسازی
FAQ/TechSkill در `seed_home_content`."""
import sys

from django.core.management.base import BaseCommand

from apps.core.models import (
    AboutPageHero,
    AboutStory,
    AboutStat,
    AboutJourneySection,
    AboutJourneyStep,
    AboutClientsSection,
)


HERO = {
    "eyebrow": "استودیوی طراحی و توسعهٔ پیکسوریا",
    "title": "داستانی که از [[۱۳۸۹]] آغاز شد",
    "description": (
        "پانزده سال است در مشهد کنار برندها هستیم؛ از طراحی لوگو و خدمات "
        "گرافیکی تا طراحی سایت و برنامه‌نویسی. این‌جا داستانِ ساخته‌شدنِ یک "
        "اعتبار است."
    ),
    "cta_primary_text": "تماس با ما",
    "cta_primary_url": "contact:contact",
    "cta_secondary_text": "خدمات ما",
    "cta_secondary_url": "services:list",
}

STORY = {
    "eyebrow": "داستان ما",
    "title": "از یک استودیوی طراحی، تا مشاورِ [[برندها]]",
    "description": (
        "«استودیوی طراحی و توسعهٔ پیکسوریا» کار خود را در سال ۱۳۸۹ آغاز کرد و "
        "از همان روز نخست، باور داشت که طراحی خوب، از اعتبار شروع می‌شود — نه "
        "از بودجه."
    ),
    "body": (
        "در این سال‌ها، پیکسوریا در زمینه‌های طراحی سایت، برنامه‌نویسی، خدمات "
        "گرافیکی و طراحی لوگو در مشهد فعالیت کرده و به‌عنوان مشاور و مجری "
        "پروژه‌های دیجیتال، در کنار شرکت‌ها و ادارات بوده است.\n"
        "برای ما هر پروژه یک امضاست؛ امضایی که باید سال‌ها در ذهن مخاطب بماند."
    ),
    "chips": "مشهد، مشاور و مجری تبلیغات، شرکت‌ها و ادارات",
    "quote": "«تصویرِ حرفه‌ای، سرمایه‌ای است که در ذهنِ مخاطب، سال‌ها بازده می‌دهد.»",
    "image_caption": "مشهد",
}

JOURNEY = {
    "eyebrow": "حوزه‌های فعالیت",
    "title": "حوزه‌ها، در یک [[مسیر]]",
    "subtitle": "از آغاز تا امروز؛ هر حوزه، یک ایستگاه در مسیرِ اعتبار.",
    "badge_icon": "award",
    "badge_text": "+۱۵ سال تجربه",
}

# ایستگاه‌های مسیر — مطابق نقشهٔ SVG طرح v2 (۵ ایستگاه).
JOURNEY_STEPS = [
    {"year": "۱۳۸۹", "title": "آغاز فعالیت", "subtitle": ""},
    {"year": "", "title": "طراحی و چاپ", "subtitle": "پوستر و اقلام تبلیغاتی چاپی"},
    {"year": "", "title": "هویت بصری و گرافیک", "subtitle": "طراحی لوگو و برندینگ کامل"},
    {"year": "", "title": "طراحی سایت", "subtitle": "وب‌سایت و نرم‌افزارهای اختصاصی"},
    {"year": "امروز", "title": "مشاور و مجری برندها", "subtitle": ""},
]

# چهار شمارندهٔ بخش آمار (روشن).
STATS = [
    {"icon": "award", "value": 15, "prefix": "+", "suffix": "", "label": "سال سابقه"},
    {
        "icon": "briefcase",
        "value": 500,
        "prefix": "+",
        "suffix": "",
        "label": "کسب‌وکار مشاوره‌شده",
    },
    {"icon": "users", "value": 135, "prefix": "", "suffix": "+", "label": "بلاگر تبلیغاتی"},
    {
        "icon": "at-sign",
        "value": 350,
        "prefix": "",
        "suffix": "+",
        "label": "پیج عمومی و تبلیغاتی کشور",
    },
]

CLIENTS_SECTION = {
    "eyebrow": "رزومه و اعتماد",
    "title": "اعتمادِ آن‌ها، [[افتخارِ ما]]",
    "subtitle": "همکاری با بانک‌ها، شرکت‌های صنعتی و کنگره‌های ملی در مشهد.",
}


def first_or_create(model, **fields):
    """Singleton helper: never overwrite content the admin already edited."""
    obj = model.objects.first()
    if obj is not None:
        return obj, False
    return model.objects.create(**fields), True


class Command(BaseCommand):
    help = "پر کردن محتوای پیش‌فرض صفحهٔ درباره ما با متن فارسیِ طرح v2"

    def handle(self, *args, **options):
        # کنسول ویندوز به‌طور پیش‌فرض cp1252 است و روی پیام‌های فارسی خطا می‌دهد.
        sys.stdout.reconfigure(encoding="utf-8")

        self.seed_hero()
        self.seed_story()
        self.seed_journey()
        self.seed_stats()
        self.seed_clients_section()

    def seed_hero(self):
        obj, created = first_or_create(AboutPageHero, **HERO)
        self.stdout.write(
            "هیرو: " + ("ساخته شد" if created else f"از قبل موجود — دست‌نخورده ({obj})")
        )

    def seed_story(self):
        obj, created = first_or_create(AboutStory, **STORY)
        self.stdout.write(
            "داستان: " + ("ساخته شد" if created else f"از قبل موجود — دست‌نخورده ({obj})")
        )

    def seed_journey(self):
        _, created = first_or_create(AboutJourneySection, **JOURNEY)
        self.stdout.write("بخش مسیر: " + ("ساخته شد" if created else "از قبل موجود — دست‌نخورده"))

        # ایستگاه‌ها بر اساس عنوان کلید هستند؛ ردیف‌های خارج از فهرست v2 مثل
        # پاکسازیِ FAQ صفحه اصلی حذف می‌شوند.
        titles = [s["title"] for s in JOURNEY_STEPS]
        stale = AboutJourneyStep.objects.exclude(title__in=titles)
        if stale.exists():
            self.stdout.write(
                f"ایستگاه‌های قدیمی حذف شدند: {', '.join(stale.values_list('title', flat=True))}"
            )
            stale.delete()
        for order, fields in enumerate(JOURNEY_STEPS):
            AboutJourneyStep.objects.get_or_create(title=fields["title"], defaults={**fields, "order": order})
        self.stdout.write(f"ایستگاه‌های مسیر: {AboutJourneyStep.objects.count()} ردیف")

    def seed_stats(self):
        # آمار قدیمیِ v1 (متن عددِ آزاد مثل «+۵۰») در طرح v2 نمایش داده نمی‌شوند؛
        # ردیف‌های خارج از فهرست جدید حذف و مفقودی‌ها ساخته می‌شوند.
        labels = [s["label"] for s in STATS]
        stale = AboutStat.objects.exclude(label__in=labels)
        if stale.exists():
            self.stdout.write(
                f"آمار قدیمی حذف شدند: {', '.join(stale.values_list('label', flat=True))}"
            )
            stale.delete()
        for order, fields in enumerate(STATS):
            AboutStat.objects.get_or_create(label=fields["label"], defaults={**fields, "order": order})
        self.stdout.write(f"آمار: {AboutStat.objects.count()} ردیف")

    def seed_clients_section(self):
        _, created = first_or_create(AboutClientsSection, **CLIENTS_SECTION)
        self.stdout.write(
            "بخش مشتریان: " + ("ساخته شد" if created else "از قبل موجود — دست‌نخورده")
        )
        self.stdout.write(
            "نکته: نام برندها از همین جدول «برندهای همکار» صفحه اصلی خوانده می‌شوند "
            "(home.ClientMarqueeItem)؛ ویرایش آن‌ها در بخش صفحه اصلی."
        )
