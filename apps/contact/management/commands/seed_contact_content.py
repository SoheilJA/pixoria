"""پر کردن محتوای پیش‌فرض صفحهٔ «تماس با ما» با متن فارسیِ طرح v2.

متن‌ها از `new/contact.html` گرفته شده‌اند. بعد از migrate اجرا شود:

    python manage.py seed_contact_content

Idempotent: سینگلتون‌ها و مجموعه‌ها وقتی از قبل وجود داشته باشند دست‌نخورده
می‌مانند (قانون «محتوای ویرایش‌شده در ادمین هرگز بازنویسی نمی‌شود»)، مگر اینکه
ردیفی دقیقاً در فهرست v2 نباشد — در آن صورت مثل پاکسازیِ FAQ صفحه اصلی حذف
می‌شود."""
import sys

from django.core.management.base import BaseCommand

from apps.contact.models import (
    ContactPageSection,
    ContactFormSection,
    ContactFormPoint,
    ContactMapSection,
    ContactFaqSection,
    ContactFaq,
    SubjectChoice,
)


PAGE_SECTION = {
    "eyebrow": "تماس با ما",
    "title": "بیایید [[گفت‌وگو]] کنیم",
    "description": (
        "تیم پیکسوریا آمادهٔ شنیدن از برند شماست؛ یک تماس، یک پیام — و مسیرِ "
        "رشد از همان‌جا شروع می‌شود."
    ),
    "response_note": "پاسخ‌گویی در روزهای کاری، حداکثر تا ۲۴ ساعت",
}

FORM_SECTION = {
    "eyebrow": "ارسال پیام",
    "title": "پیامِ شما، شروعِ یک [[همکاری]]",
    "description": (
        "فرم را پر کنید؛ کارشناسان پیکسوریا در اولین فرصت با شما تماس می‌گیرند."
    ),
    "button_text": "ارسال پیام",
    "note": "اطلاعات شما فقط برای پاسخ‌گویی استفاده می‌شود.",
}

# مزیت‌های کنار فرم (آیکون + متن).
FORM_POINTS = [
    {"icon": "message-circle", "text": "مشاورهٔ اولیهٔ رایگان"},
    {"icon": "map-pin", "text": "مشهد"},
    {"icon": "clock", "text": "پاسخ‌گویی روزهای کاری"},
]

MAP_SECTION = {
    "eyebrow": "حضور فیزیکی",
    "title": "یک دفتر، [[یک تیم متعهد]]",
    "subtitle": (
        "اجرا و نظارت بر کمپین‌ها و همایش‌ها، از دفتر مرکزی پیکسوریا در مشهد."
    ),
    "office_name": "مشهد",
    "office_note": "دفتر مرکزی و تیم اجرایی",
    "coverage_note": "خدمات در سراسر ایران · اجرا و نظارت مستقیم",
}

FAQ_SECTION = {
    "eyebrow": "پرسش‌های پرتکرار",
    "title": "قبل از تماس، [[بدانید]]",
    "footer_question": "پاسخ‌تان را پیدا نکردید؟",
    "footer_cta_text": "ارسال پیام",
}

# چهار پرسشِ پرتکرارِ طرح v2.
FAQS = [
    {
        "question": "مشاورهٔ پیکسوریا رایگان است؟",
        "answer": (
            "بله؛ جلسهٔ اولِ آشنایی و بررسی نیاز شما کاملاً رایگان است و پس از "
            "آن، پیشنهاد شفاف و مکتوب دریافت می‌کنید."
        ),
    },
    {
        "question": "برای شروع همکاری چه اطلاعاتی لازم است؟",
        "answer": (
            "معرفی کوتاهِ کسب‌وکار، هدفِ تبلیغاتی و بازهٔ زمانی موردنظر کافی "
            "است؛ بقیه را در جلسهٔ مشاوره با هم می‌سازیم."
        ),
    },
    {
        "question": "زمان اجرای پروژه‌ها چقدر است؟",
        "answer": (
            "بسته به نوع خدمت متفاوت است؛ زمان‌بندی دقیق و مرحله‌به‌مرحله پیش "
            "از شروع، به‌صورت مکتوب اعلام می‌شود."
        ),
    },
    {
        "question": "پس از اجرا هم پشتیبانی می‌کنید؟",
        "answer": "بله؛ امنیت و پشتیبانی کامل، یکی از ستون‌های همکاری با پیکسوریا است.",
    },
]

# گزینه‌های موضوعِ فرم تماس.
SUBJECTS = [
    "مشاورهٔ خدمات",
    "درخواست سفارش پروژه",
    "همکاری",
    "سایر",
]


def first_or_create(model, **fields):
    """Singleton helper: never overwrite content the admin already edited."""
    obj = model.objects.first()
    if obj is not None:
        return obj, False
    return model.objects.create(**fields), True


class Command(BaseCommand):
    help = "پر کردن محتوای پیش‌فرض صفحهٔ تماس با ما با متن فارسیِ طرح v2"

    def handle(self, *args, **options):
        # کنسول ویندوز به‌طور پیش‌فرض cp1252 است و روی پیام‌های فارسی خطا می‌دهد.
        sys.stdout.reconfigure(encoding="utf-8")

        self.seed_page_section()
        self.seed_form_section()
        self.seed_map_section()
        self.seed_faq_section()
        self.seed_subjects()

    def seed_page_section(self):
        _, created = first_or_create(ContactPageSection, **PAGE_SECTION)
        self.stdout.write(
            "هیرو: " + ("ساخته شد" if created else "از قبل موجود — دست‌نخورده")
        )

    def seed_form_section(self):
        section, created = first_or_create(ContactFormSection, **FORM_SECTION)
        self.stdout.write(
            "بخش فرم: " + ("ساخته شد" if created else "از قبل موجود — دست‌نخورده")
        )

        # مزیت‌ها بر اساس متن کلید هستند؛ ردیف‌های خارج از فهرست v2 حذف می‌شوند.
        texts = [p["text"] for p in FORM_POINTS]
        stale = ContactFormPoint.objects.exclude(text__in=texts)
        if stale.exists():
            self.stdout.write(
                f"مزیت‌های قدیمی حذف شدند: {', '.join(stale.values_list('text', flat=True))}"
            )
            stale.delete()
        for order, fields in enumerate(FORM_POINTS):
            ContactFormPoint.objects.get_or_create(
                text=fields["text"],
                defaults={**fields, "order": order, "section": section},
            )
        self.stdout.write(f"مزیت‌های فرم: {ContactFormPoint.objects.count()} ردیف")

    def seed_map_section(self):
        _, created = first_or_create(ContactMapSection, **MAP_SECTION)
        self.stdout.write(
            "بخش نقشه: " + ("ساخته شد" if created else "از قبل موجود — دست‌نخورده")
        )

    def seed_faq_section(self):
        _, created = first_or_create(ContactFaqSection, **FAQ_SECTION)
        self.stdout.write(
            "بخش پرسش‌ها: " + ("ساخته شد" if created else "از قبل موجود — دست‌نخورده")
        )

        questions = [f["question"] for f in FAQS]
        stale = ContactFaq.objects.exclude(question__in=questions)
        if stale.exists():
            self.stdout.write(
                f"پرسش‌های قدیمی حذف شدند: {', '.join(stale.values_list('question', flat=True))}"
            )
            stale.delete()
        for order, fields in enumerate(FAQS):
            ContactFaq.objects.get_or_create(
                question=fields["question"], defaults={**fields, "order": order}
            )
        self.stdout.write(f"پرسش‌های پرتکرار: {ContactFaq.objects.count()} ردیف")

    def seed_subjects(self):
        for order, label in enumerate(SUBJECTS):
            SubjectChoice.objects.get_or_create(label=label, defaults={"order": order})
        self.stdout.write(f"موضوع‌های پیام: {SubjectChoice.objects.count()} ردیف")
