"""Seed realistic Persian default content for the homepage and shared chrome.

Run after migrating so the site looks complete out of the box:

    python manage.py seed_home_content

Idempotent: existing rows are left alone, so it is safe to re-run after adding
new sections. Content is Persian only — no lorem ipsum.
"""

import sys

from django.core.management.base import BaseCommand

from apps.core.models import SiteSettings, SocialLink
from apps.home.models import (
    HeaderSettings,
    NavItem,
    HeroSection,
    HeroStat,
    HeroMarqueeItem,
    FeaturedWorkSection,
    ServicesSection,
    ClientMarqueeItem,
    ManifestoSection,
    CTASection,
    LatestArticlesSection,
    HomeSection,
    HomeAboutSection,
    HomeAboutStat,
    TrustedSection,
    TestimonialSection,
    StatsSection,
    StatItem,
    ProcessSection,
    ProcessStep,
    WhySection,
    WhyFeature,
    TechSection,
    TechSkill,
    FaqSection,
    FaqItem,
)


# کلیدهایی که پارشالشان وجود دارد و در صفحه رندر می‌شوند. هر بار که یک
# پارشال جدید اضافه می‌شود، کلیدش از اینجا روشن می‌شود.
RENDERED_SECTIONS = {
    "hero",
    "about",
    "services",
    "trusted",
    "portfolio",
    "why",
    "process",
    "testimonials",
    "tech",
    "stats",
    "blog",
    "faq",
}

# ترتیب پیش‌فرض بخش‌ها در صفحه — مطابق جریان تجربهٔ کاربری طرح v2.
SECTION_ORDER = {
    "hero": 0,
    "about": 10,
    "services": 20,
    "trusted": 30,
    "portfolio": 40,
    "why": 50,
    "process": 60,
    "testimonials": 70,
    "tech": 80,
    "stats": 90,
    "blog": 100,
    "faq": 110,
}

SECTION_TITLES = {
    "hero": "هیرو",
    "about": "درباره ما",
    "services": "خدمات",
    "trusted": "برندهای همکار",
    "portfolio": "نمونه‌کارها",
    "why": "چرا پیکسوریا",
    "process": "فرآیند کار",
    "testimonials": "نظرات مشتریان",
    "tech": "تکنولوژی‌ها و مهارت‌ها",
    "stats": "آمار و ارقام",
    "blog": "آخرین مقالات",
    "faq": "سوالات متداول",
}


def first_or_create(model, **fields):
    """Singleton helper: never overwrite content the admin already edited."""
    obj = model.objects.first()
    if obj is not None:
        return obj, False
    return model.objects.create(**fields), True


class Command(BaseCommand):
    help = "پر کردن محتوای پیش‌فرض صفحه اصلی و هدر"

    def handle(self, *args, **options):
        # کنسول ویندوز به‌طور پیش‌فرض cp1252 است و روی پیام‌های فارسی خطا می‌دهد.
        sys.stdout.reconfigure(encoding="utf-8")

        self.seed_header()
        self.seed_hero()
        self.seed_sections()
        self.seed_stats()
        self.seed_process()
        self.seed_why()
        self.seed_tech()
        self.seed_faq()
        self.seed_home_sections()
        self.seed_services()
        self.seed_site()
        self.stdout.write(self.style.SUCCESS("محتوای پیش‌فرض پیکسوریا آماده شد."))

    # ── Header: CTA + nav items ──
    def seed_header(self):
        _, created = first_or_create(
            HeaderSettings,
            cta_text="مشاوره رایگان",
            cta_url="contact:contact",
            show_cta=True,
        )
        self.log("هدر", created)

        defaults = [
            ("خانه", "home:home", 0),
            ("نمونه‌کارها", "portfolio:list", 10),
            ("خدمات", "services:list", 20),
            ("بلاگ", "blog:list", 30),
            ("درباره ما", "core:about", 40),
            ("تماس", "contact:contact", 50),
        ]
        created_count = 0
        for title, url, order in defaults:
            if not NavItem.objects.filter(url=url).exists():
                NavItem.objects.create(title=title, url=url, order=order)
                created_count += 1
        if created_count:
            self.stdout.write(f"  + {created_count} آیتم منو")

    # ── Hero ──
    def seed_hero(self):
        _, created = first_or_create(
            HeroSection,
            eyebrow="استودیوی طراحی و توسعه · از سال ۱۳۸۹",
            title="تصویری حرفه‌ای،[[برندی ماندگار]]",
            description=(
                "پیکسوریا پانزده سال است در مشهد کنار برندهاست؛ از طراحی سایت "
                "و برنامه‌نویسی تا خدمات گرافیکی و طراحی لوگو — تا برند شما "
                "همان‌قدر که شایسته است، دیده شود."
            ),
            cta_primary_text="مشاوره رایگان",
            cta_primary_url="#contact",
            cta_secondary_text="مشاهده نمونه‌کارها",
            cta_secondary_url="#portfolio",
        )
        self.log("هیرو", created)

        stats = [
            ("+۵۰۰", "کسب‌وکار مشاوره‌شده", "", 0),
            ("۱۳۵+", "بلاگر تبلیغاتی", "", 10),
            ("مشهد", "", "map-pin", 20),
        ]
        added = 0
        for value, label, icon, order in stats:
            if not HeroStat.objects.filter(value=value, label=label).exists():
                HeroStat.objects.create(value=value, label=label, icon=icon, order=order)
                added += 1
        if added:
            self.stdout.write(f"  + {added} آمار هیرو")

        marquee = [
            "طراحی وب‌سایت",
            "توسعهٔ فرانت‌اند",
            "طراحی لوگو و هویت بصری",
            "گرافیک دیجیتال",
            "سئو و بهینه‌سازی",
            "تجربهٔ کاربری",
        ]
        added = 0
        for i, text in enumerate(marquee):
            if not HeroMarqueeItem.objects.filter(text=text).exists():
                HeroMarqueeItem.objects.create(text=text, order=i * 10)
                added += 1
        if added:
            self.stdout.write(f"  + {added} آیتم مارکی هیرو")

    # ── Section singletons ──
    def seed_sections(self):
        _, c = first_or_create(
            HomeAboutSection,
            eyebrow="درباره پیکسوریا",
            title="پانزده سال تجربه، یک هدف:[[برندی ماندگار]]",
            paragraph_one=(
                "«استودیوی طراحی و توسعهٔ پیکسوریا» از سال ۱۳۸۹ کار خود را آغاز کرده و "
                "در حوزه‌های طراحی سایت، برنامه‌نویسی، خدمات گرافیکی و طراحی لوگو "
                "در مشهد فعالیت می‌کند."
            ),
            paragraph_two=(
                "در این سال‌ها، پیکسوریا به‌عنوان مشاور و مجری تبلیغات در کنار "
                "شرکت‌ها و ادارات بوده است؛ با یک هدف روشن: ساختن تصویری حرفه‌ای "
                "و اعتباری ماندگار برای برند شما."
            ),
            chips="طراحی سایت، برنامه‌نویسی، خدمات گرافیکی، طراحی لوگو",
            footer_label="PIXORIA · EST. 2010",
        )
        self.log("درباره ما", c)

        about_stats = [
            ("award", "15", "", "+", "سال سابقه"),
            ("briefcase", "500", "", "+", "کسب‌وکار مشاوره‌شده"),
            ("users", "135", "", "+", "بلاگر تبلیغاتی"),
            ("at-sign", "350", "", "+", "پیج عمومی و تبلیغاتی کشور"),
        ]
        added = 0
        for icon, value, prefix, suffix, label in about_stats:
            if not HomeAboutStat.objects.filter(label=label).exists():
                HomeAboutStat.objects.create(
                    icon=icon, value=value, prefix=prefix, suffix=suffix, label=label,
                    order=about_stats.index((icon, value, prefix, suffix, label)) * 10,
                )
                added += 1
        if added:
            self.stdout.write(f"  + {added} شمارندهٔ درباره ما")

        _, c = first_or_create(
            TrustedSection,
            eyebrow="رزومه و اعتماد",
            title="برندهایی که به ما اعتماد کردند",
            description=(
                "همکاری با بانک‌ها، شرکت‌های صنعتی و کنگره‌های ملی؛ اعتبارِ ما، "
                "امضای آن‌هاست."
            ),
            footer_label="TRUSTED PARTNERS · SINCE 2010",
        )
        self.log("برندهای همکار", c)

        _, c = first_or_create(
            TestimonialSection,
            eyebrow="نظرات مشتریان",
            title="آنچه مشتریان [[می‌گویند]]",
        )
        self.log("نظرات مشتریان", c)

        _, c = first_or_create(
            FeaturedWorkSection,
            eyebrow="نمونه‌کارها",
            title="گزیدهٔ [[پروژه‌ها]]",
            description=(
                "هر پروژه، یک داستان از ایده تا اجراست. با فیلتر، پروژه‌های هر "
                "خدمت را جداگانه ببینید."
            ),
        )
        self.log("نمونه کارها", c)

        _, c = first_or_create(
            ServicesSection,
            eyebrow="خدمات ما",
            title="از ایده تا اجرا، [[زیر یک سقف]]",
            description=(
                "چهار سرویس اصلی، یک استاندارد: کیفیتِ بی‌تعارف. هر پروژه در "
                "پیکسوریا با وسواس یک کارگاه هنری پیش می‌رود."
            ),
        )
        self.log("خدمات", c)

        _, c = first_or_create(
            ManifestoSection,
            label="چرا پیکسوریا",
            title="جزئیات، تفاوت اصلی است",
            highlighted_word="جزئیات",
            paragraph_one=(
                "ما به کوچک‌ترین جزئیات اهمیت می‌دهیم؛ از فاصلهٔ بین حروف تا سرعت "
                "بارگذاری هر تصویر. چون می‌دانیم کیفیت، حاصلِ توجه به چیزی است که "
                "بقیه از آن می‌گذرند."
            ),
            paragraph_two=(
                "تیم ما طراح و توسعه‌دهنده است، اما قبل از همه شریک کاری شما. "
                "شفاف می‌گوییم، به‌موقع تحویل می‌دهیم و بعد از انتشار هم کنارتان می‌مانیم."
            ),
            signature_name="پیکسوریا",
            signature_title="استودیوی طراحی دیجیتال",
        )
        self.log("مانیفست", c)

        _, c = first_or_create(
            CTASection,
            eyebrow="برند شما، امضای ما",
            title="بیایید [[برندِ شما]] را ماندگار کنیم",
            description="از یک گفت‌وگوی ساده شروع می‌شود؛ مشاورهٔ رایگان، بدون تعهد.",
            email="info@pixoria.ir",
            phone="۰۵۱-۳۶۰۴۴۹۸۹",
        )
        self.log("CTA", c)

        _, c = first_or_create(
            LatestArticlesSection,
            eyebrow="مجلهٔ پیکسوریا",
            title="آخرین [[نوشته‌ها]]",
            description="",
        )
        self.log("آخرین مقالات", c)

        clients = [
            ("رفاه", "بانک رفاه", "gold"),
            ("پپسی", "پپسی خراسان", "royal"),
            ("تجارت", "بانک تجارت", "gold"),
            ("هواآوی", "شرکت هواآوی", "royal"),
            ("شهر", "بانک شهر", "gold"),
            ("توس", "شرکت توس / مبنا", "royal"),
            ("کنگره", "کنگرهٔ ملی ساخت بیمارستان", "gold"),
        ]
        added = 0
        for i, (mark, name, accent) in enumerate(clients):
            if not ClientMarqueeItem.objects.filter(name=name).exists():
                ClientMarqueeItem.objects.create(
                    mark=mark, name=name, accent=accent, order=i * 10
                )
                added += 1
        # برندهای v1 که در طرح جدید نیستند از مارکویی حذف می‌شوند.
        names = {name for _, name, _ in clients}
        stale = ClientMarqueeItem.objects.exclude(name__in=names)
        removed = stale.delete()[0]
        if added:
            self.stdout.write(f"  + {added} برند همکار")
        if removed:
            self.stdout.write(f"  - {removed} برند قدیمی حذف شد")

    # ── Stats / counters ──
    def seed_stats(self):
        _, c = first_or_create(
            StatsSection,
            eyebrow="دستاوردها",
            title="پیکسوریا [[در یک نگاه]]",
            description="",
        )
        self.log("آمار", c)

        stats = [
            ("calendar-days", "", "", "15", "سال تجربهٔ فعال"),
            ("rocket", "", "+", "500", "پروژهٔ تحویل‌شده"),
            ("smile", "", "٪", "98", "رضایت کارفرمایان"),
            ("clock", "", "/۷", "24", "پشتیبانی بی‌وقفه"),
        ]
        added = 0
        for i, (icon, prefix, suffix, value, label) in enumerate(stats):
            if not StatItem.objects.filter(label=label).exists():
                StatItem.objects.create(
                    icon=icon,
                    prefix=prefix,
                    suffix=suffix,
                    value=value,
                    label=label,
                    description="",
                    order=i * 10,
                )
                added += 1
        if added:
            self.stdout.write(f"  + {added} آیتم آمار")

    # ── Process ──
    def seed_process(self):
        _, c = first_or_create(
            ProcessSection,
            eyebrow="روش کار ما",
            title="از ایده تا [[تحویل]] در پنج گام",
            description=(
                "هر پروژه یک مسیر روشن دارد؛ از اولین گفت‌وگو تا روزی که برندتان "
                "دیده می‌شود."
            ),
        )
        self.log("فرآیند", c)

        steps = [
            (
                "message-circle",
                "مشاوره",
                "گفت‌وگوی اولیه، شناخت برند و تعیین هدف و بودجهٔ پروژه.",
            ),
            (
                "search",
                "تحقیق و استراتژی",
                "بررسی رقبا، مخاطب و بازار تا تصمیم‌های طراحی داده‌محور باشد.",
            ),
            (
                "pen-tool",
                "طراحی",
                "کنسپت، نمونهٔ بصری و بازخورد؛ تا طرح نهایی قلب تپندهٔ پروژه شود.",
            ),
            (
                "code-xml",
                "توسعه",
                "کدنویسی، تست و انتشار؛ با بازخوردِ مرحله‌بندی‌شده در هر گام.",
            ),
            (
                "party-popper",
                "تحویل و رشد",
                "تحویل نهایی، آموزش تیم شما و همراهی برای رشدِ پایدار برند.",
            ),
        ]
        added = 0
        for i, (icon, title, desc) in enumerate(steps):
            if not ProcessStep.objects.filter(title=title).exists():
                ProcessStep.objects.create(
                    icon=icon, title=title, description=desc, order=i * 10
                )
                added += 1
        if added:
            self.stdout.write(f"  + {added} مرحله فرآیند")

    # ── Why Pixoria (bento) ──
    def seed_why(self):
        _, c = first_or_create(
            WhySection,
            eyebrow="چرا پیکسوریا؟",
            title="شش دلیل برای [[انتخاب ما]]",
            description="اعتبار، ساخته نمی‌شود؛ همکاری به همکاری، پروژه به پروژه به دست می‌آید.",
        )
        self.log("چرا پیکسوریا", c)

        features = [
            ("badge-check", "اعتبار و اعتماد", "سال‌ها همکاری با بانک‌ها و شرکت‌های معتبر، ضمانتِ کیفیت ماست."),
            ("gem", "تمایز از رقبا", "خلاقیتِ هدفمند، برند شما را از رقبا متمایز می‌کند."),
            ("zap", "تحویل به‌موقع", "هر مرحله با تایم‌لاین شفاف پیش می‌رود؛ تعهد به زمان، اصل کارِ ماست."),
            ("trending-up", "رشد و دیده‌شدن برند", "کمپین‌هایی که دیده می‌شوند و فروش را رشد می‌دهند."),
            ("shield-check", "امنیت و پشتیبانی کامل", "از مشاوره تا اجرا و پشتیبانی، همیشه کنار شما هستیم."),
            ("heart-handshake", "همراهی پس از تحویل", "پروژه با تحویل تمام نمی‌شود؛ تا رشد برندتان همراهتان هستیم."),
        ]
        added = 0
        for i, (icon, title, desc) in enumerate(features):
            if not WhyFeature.objects.filter(title=title).exists():
                WhyFeature.objects.create(
                    icon=icon, title=title, description=desc, size="", order=i * 10
                )
                added += 1
        if added:
            self.stdout.write(f"  + {added} ویژگی")

    # ── Tech / skills ──
    def seed_tech(self):
        _, c = first_or_create(
            TechSection,
            eyebrow="ابزارها و فناوری‌ها",
            title="با بهترین [[ابزارها]] کار می‌کنیم",
            description="",
        )
        self.log("تکنولوژی", c)

        # دو ردیف مارکی طرح v2 — نیمهٔ اول در ردیف اول و نیمهٔ دوم در ردیف دوم.
        skills = [
            ("figma", "Figma"),
            ("code-2", "React"),
            ("square-code", "Next.js"),
            ("braces", "TypeScript"),
            ("wind", "Tailwind"),
            ("box", "Node.js"),
            ("pen-tool", "Illustrator"),
            ("image", "Photoshop"),
            ("film", "After Effects"),
            ("palette", "InDesign"),
            ("orbit", "Three.js"),
            ("terminal", "Python"),
        ]
        added = 0
        for i, (icon, name) in enumerate(skills):
            if not TechSkill.objects.filter(name=name).exists():
                TechSkill.objects.create(
                    name=name, icon=icon, category="", order=i * 10
                )
                added += 1
        # ابزارهای v1 که در طرح جدید نیستند حذف می‌شوند.
        names = {name for _, name in skills}
        removed = TechSkill.objects.exclude(name__in=names).delete()[0]
        if added:
            self.stdout.write(f"  + {added} مهارت")
        if removed:
            self.stdout.write(f"  - {removed} ابزار قدیمی حذف شد")

    # ── FAQ ──
    def seed_faq(self):
        _, c = first_or_create(
            FaqSection,
            eyebrow="پرسش‌های متداول",
            title="هر سوالی [[دارید]]",
            description="پاسخ پرتکرارترین پرسش‌ها؛ اگر چیزی جا مانده، منتظر پیام شما هستیم.",
        )
        self.log("سوالات متداول", c)

        items = [
            (
                "هزینهٔ طراحی یک سایت چقدر است؟",
                "بستگی به دامنهٔ پروژه دارد: سایت شرکتی، فروشگاهی یا درگاه اختصاصی. "
                "پس از یک مشاورهٔ رایگان و تعیین نیازمندی‌ها، پیش‌فاکتور شفاف و "
                "مرحله‌بندی‌شده تحویل شما می‌شود. هیچ هزینهٔ پنهانی وجود ندارد.",
            ),
            (
                "پروژه از سفارش تا تحویل چقدر طول می‌کشد؟",
                "یک سایت شرکتی حدود ۲ تا ۴ هفته، پروژه‌های توسعهٔ نرم‌افزار بین ۶ تا "
                "۱۲ هفته و طراحی لوگو بین ۱ تا ۳ هفته زمان می‌برد. تایم‌لاین هر مرحله "
                "از روز اول با شما هماهنگ می‌شود.",
            ),
            (
                "بعد از تحویل، پشتیبانی دارید؟",
                "بله. همهٔ پروژه‌ها با دورهٔ پشتیبانی رایگان تحویل می‌شوند و پس از آن "
                "می‌توانید قرارداد پشتیبانی ماهانه ببندید؛ از آپدیت محتوا تا نظارت "
                "امنیتی و پشتیبانی فنی ۲۴/۷.",
            ),
            (
                "طراحی لوگو چند طرح پیشنهادی می‌دهد؟",
                "بسته به پروژه، ۲ تا ۴ کنسپت اولیه ارائه می‌شود؛ سپس روی طرح انتخابی "
                "تا سه مرحله اصلاح انجام می‌گیرد. خروجی نهایی شامل فایل‌های وکتور، "
                "رنگی، تک‌رنگ و راهنمای کامل استفاده از لوگوست.",
            ),
            (
                "فایل‌های آمادهٔ چاپ را هم تحویل می‌دهید؟",
                "بله. همهٔ طرح‌های گرافیک با پروفایل رنگی CMYK، رزوه و حاشیهٔ برش "
                "تحویل می‌شوند تا چاپخانه بدون مشکل آن را اجرا کند. در صورت نیاز، "
                "خودمان تا تحویلِ چاپ هم پروژه را دنبال می‌کنیم.",
            ),
            (
                "قرارداد و فاکتور رسمی صادر می‌شود؟",
                "بله. پیکسوریا یک استودیوی رسمی است؛ قرارداد، پیش‌فاکتور و فاکتور برای "
                "همهٔ مراحل صادر می‌شود و پرداخت‌ها به‌صورت مرحله‌بندی‌شده و شفاف "
                "انجام می‌گیرند.",
            ),
        ]
        added = 0
        for i, (question, answer) in enumerate(items):
            if not FaqItem.objects.filter(question=question).exists():
                FaqItem.objects.create(
                    question=question, answer=answer, order=i * 10
                )
                added += 1
        # سوالات v1 که در طرح جدید نیستند حذف می‌شوند.
        questions = {q for q, _ in items}
        removed = FaqItem.objects.exclude(question__in=questions).delete()[0]
        if added:
            self.stdout.write(f"  + {added} سوال متداول")
        if removed:
            self.stdout.write(f"  - {removed} سوال قدیمی حذف شد")

    # ── HomeSection rows: order + visibility of every partial ──
    def seed_home_sections(self):
        created = 0
        for key, title in SECTION_TITLES.items():
            if key not in RENDERED_SECTIONS:
                continue
            _, c = HomeSection.objects.get_or_create(
                key=key,
                defaults={
                    "title": title,
                    "order": SECTION_ORDER[key],
                    "is_active": True,
                },
            )
            created += int(c)
        if created:
            self.stdout.write(f"  + {created} بخش صفحه اصلی")

    # ── Services: تصویرسازی و برچسب کارت‌های v2 ──
    def seed_services(self):
        from apps.services.models import Service

        v2 = {
            "طراحی سایت": dict(
                icon="monitor-smartphone", visual="browser", card_span="wide",
                chips="واکنش‌گرا، سئو-friendly، پشتیبانی مستمر",
                badge="۹۹/۱۰۰ · Core Web Vitals",
            ),
            "برنامه‌نویسی": dict(
                icon="code-xml", visual="terminal", card_span="narrow",
                chips="", badge="CI/CD خودکار",
            ),
            "خدمات گرافیکی": dict(
                icon="palette", visual="palette", card_span="narrow",
                chips="", badge="",
            ),
            "طراحی لوگو": dict(
                icon="diamond", visual="diamond", card_span="wide",
                chips="کنسپت اختصاصی، فایل وکتور، راهنمای برند",
                badge="هویت بصری",
            ),
        }
        updated = 0
        for title, fields in v2.items():
            service = Service.objects.filter(title=title).first()
            if service is None:
                continue
            changed = False
            for key, value in fields.items():
                if getattr(service, key) != value:
                    setattr(service, key, value)
                    changed = True
            if changed:
                service.save()
                updated += 1
        if updated:
            self.stdout.write(f"  ~ {updated} خدمت به طرح v2 به‌روز شد")

    # ── Site settings + socials (only when the table is empty) ──
    def seed_site(self):
        if SiteSettings.objects.exists():
            return
        SiteSettings.objects.create(
            site_name="پیکسوریا",
            site_description="استودیو طراحی و توسعهٔ محصولات دیجیتال",
            tagline="هویتی درخشان، اعتباری ماندگار.",
            footer_description="استودیو طراحی و توسعه",
            email="info@pixoria.ir",
            phone="۰۵۱-۳۶۰۴۴۹۸۹",
            phone_secondary="۰۹۱۵-۶۵۰-۰۰-۱۶",
            address="مشهد، ایران",
            website="https://www.pixoria.ir",
            established_year="۱۳۸۹",
            status="آماده همکاری",
            mega_title="چهار سرویس حرفه‌ای، یک برند ماندگار",
            mega_description=(
                "از طراحی رابط کاربری تا توسعهٔ نرم‌افزار — تیم پیکسوریا برای رشد "
                "کسب‌وکار شما"
            ),
            trust_first_title="اینماد",
            trust_first_subtitle="درگاه امن پرداخت",
            trust_second_title="ساماندهی",
            trust_second_subtitle="ثبت رسمی کسب‌وکار",
            trust_note="لوگوی اینماد و ساماندهی پس از دریافت در همین قسمت قرار می‌گیرد.",
        )
        self.stdout.write("  + تنظیمات سایت")

        socials = [
            ("IG", "اینستاگرام", "instagram", "https://instagram.com/pixoria", 10),
            ("LI", "لینکدین", "linkedin", "https://linkedin.com/company/pixoria", 20),
            ("TG", "تلگرام", "send", "https://t.me/pixoria", 30),
            ("WEB", "وب‌سایت", "globe", "https://www.pixoria.ir", 40),
        ]
        for label, name, icon, url, order in socials:
            if not SocialLink.objects.filter(url=url).exists():
                SocialLink.objects.create(
                    label=label, name=name, icon=icon, url=url, order=order
                )
        self.stdout.write("  + شبکه‌های اجتماعی")

    def log(self, name, created):
        if created:
            self.stdout.write(f"  + {name}")
