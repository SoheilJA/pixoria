"""Seed realistic Persian default content for the homepage and shared chrome.

Run after migrating so the site looks complete out of the box:

    python manage.py seed_home_content

Idempotent: existing rows are left alone, so it is safe to re-run after adding
new sections. Content is Persian only — no lorem ipsum.
"""

from django.core.management.base import BaseCommand

from apps.core.models import SiteSettings, SocialLink
from apps.home.models import (
    HeaderSettings,
    NavItem,
    HeroSection,
    HeroMarqueeItem,
    FeaturedWorkSection,
    ServicesSection,
    ClientMarqueeItem,
    ManifestoSection,
    CTASection,
    LatestArticlesSection,
    HomeSection,
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
    ContactSection,
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
    "contact",
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
    "contact": 120,
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
    "contact": "فرم تماس سریع",
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
        self.seed_header()
        self.seed_hero()
        self.seed_sections()
        self.seed_stats()
        self.seed_process()
        self.seed_why()
        self.seed_tech()
        self.seed_faq()
        self.seed_contact()
        self.seed_home_sections()
        self.seed_site()
        self.stdout.write(self.style.SUCCESS("محتوای پیش‌فرض پیکسوریا آماده شد."))

    # ── Header: CTA + nav items ──
    def seed_header(self):
        _, created = first_or_create(
            HeaderSettings,
            cta_text="شروع پروژه",
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
            title="ایده‌هایت را به محصول می‌سازیم",
            description=(
                "پیکسوریا استودیوی طراحی و توسعهٔ محصولات دیجیتال است؛ از هویت بصری و "
                "طراحی رابط کاربری تا کدنویسی و انتشار. کنارتان هستیم تا ایده‌ای که در "
                "ذهن دارید، در دست کاربران بنشیند."
            ),
        )
        self.log("هیرو", created)

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
            FeaturedWorkSection,
            title="کارهایی که با افتخار ساخته‌ایم",
            description=(
                "هر پروژه برای ما فراتر از یک تحویل است؛ پایه‌ای برای رشد کسب‌وکار "
                "مشتری‌مان. نمونه‌کارهای منتخب را اینجا ببینید."
            ),
        )
        self.log("نمونه کارها", c)

        _, c = first_or_create(
            ServicesSection,
            title="خدمتی برای هر مرحلهٔ رشد شما",
            description=(
                "از اولین اسکچ تا انتشار و پشتیبانی، در هر گام مسیر کنارتان هستیم. "
                "حوزه‌های کاری ما را ببینید و شروع کنید."
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
            title="پروژه‌ای در ذهن دارید؟",
            description=(
                "کافی است یک پیام کوتاه بفرستید؛ در کوتاه‌ترین زمان با شما تماس "
                "می‌گیریم و مسیر همکاری را هم‌وضع می‌کنیم."
            ),
            email="hello@pixoria.ir",
            phone="۰۵۱-۱۲۳۴۵۶۷۸",
        )
        self.log("CTA", c)

        _, c = first_or_create(
            LatestArticlesSection,
            subtitle="بلاگ پیکسوریا",
            title="آخرین نوشته‌های ما",
            description=(
                "تجربه‌ها، چالش‌ها و یادگیری‌هایمان دربارهٔ طراحی، کد و رشد محصول "
                "دیجیتال را اینجا می‌نویسیم."
            ),
        )
        self.log("آخرین مقالات", c)

        clients = ["دیجی‌کالا", "اسنپ", "تپسی", "اولین", "بانک پاسارگاد", "زیرالسرویس"]
        added = 0
        for i, name in enumerate(clients):
            if not ClientMarqueeItem.objects.filter(name=name).exists():
                ClientMarqueeItem.objects.create(name=name, order=i * 10)
                added += 1
        if added:
            self.stdout.write(f"  + {added} برند همکار")

    # ── Stats / counters ──
    def seed_stats(self):
        _, c = first_or_create(
            StatsSection,
            subtitle="آمار و ارقام",
            title="عددها حرف نمی‌زنند، کار می‌کنند",
            description=(
                "به جای وعده‌های بزرگ، به آنچه ساخته‌ایم نگاه کنید. این هم خلاصه‌ای "
                "کوتاه از مسیر پیکسوریا تا امروز."
            ),
        )
        self.log("آمار", c)

        stats = [
            ("+", "", "۱۲۰", "پروژهٔ تحویل‌شده", "وب‌سایت، فروشگاه و اپلیکیشن"),
            ("", "٪", "۹۸", "رضایت مشتریان", "بر اساس نظرات پس از تحویل"),
            ("", "", "۶", "سال تجربه", "از ۱۳۹۸ تا امروز"),
            ("+", "", "۴۰", "برند همکار", "از استارتاپ تا سازمانی"),
        ]
        added = 0
        for i, (prefix, suffix, value, label, desc) in enumerate(stats):
            if not StatItem.objects.filter(label=label).exists():
                StatItem.objects.create(
                    prefix=prefix,
                    suffix=suffix,
                    value=value,
                    label=label,
                    description=desc,
                    order=i * 10,
                )
                added += 1
        if added:
            self.stdout.write(f"  + {added} آیتم آمار")

    # ── Process ──
    def seed_process(self):
        _, c = first_or_create(
            ProcessSection,
            subtitle="فرآیند کار",
            title="از ایده تا تحویل، شفاف و مرحله‌به‌مرحله",
            description=(
                "هیچ پروژه‌ای در تاریکی پیش نمی‌رود. هر گام را از قبل می‌دانید، "
                "در هر مرحله بازخورد می‌دهید و دقیقاً می‌دانید کجا هستید."
            ),
        )
        self.log("فرآیند", c)

        steps = [
            (
                "کشف و استراتژی",
                "با یک گفت‌وگوی عمیق شروع می‌کنیم؛ هدف، مخاطب و رقبا را می‌شناسیم، "
                "نیازهای واقعی را پیدا می‌کنیم و نقشهٔ راه پروژه را با هم می‌کشیم.",
            ),
            (
                "طراحی و هویت بصری",
                "از اسکچ و وایرفریم شروع می‌کنیم تا طراحی نهایی. رنگ، تایپوگرافی و "
                "هویت بصری برند در این مرحله شکل می‌گیرد و بازخورد شما در آن نقش دارد.",
            ),
            (
                "توسعه و ساخت",
                "طراحی را به کدی تمیز، سریع و واکنش‌گرا تبدیل می‌کنیم. روی مرورگرها و "
                "دستگاه‌های مختلف تست می‌کنیم تا همه‌چیز مثل ساعت کار کند.",
            ),
            (
                "انتشار و رشد",
                "پروژه را منتشر می‌کنیم، داده‌ها را اندازه می‌گیریم و بهبود می‌دهیم. "
                "بعد از تحویل هم کنارتان می‌مانیم تا رشد متوقف نشود.",
            ),
        ]
        added = 0
        for i, (title, desc) in enumerate(steps):
            if not ProcessStep.objects.filter(title=title).exists():
                ProcessStep.objects.create(
                    title=title, description=desc, order=i * 10
                )
                added += 1
        if added:
            self.stdout.write(f"  + {added} مرحله فرآیند")

    # ── Why Pixoria (bento) ──
    def seed_why(self):
        _, c = first_or_create(
            WhySection,
            subtitle="چرا پیکسوریا",
            title="با ما کار کردن، فرق دارد",
            description=(
                "ما پیمانکار نیستیم؛ شریک کاری شما هستیم. این هم چند دلیل کوچک که "
                "تیم‌ها ما را انتخاب می‌کنند و به ما اعتماد می‌کنند."
            ),
        )
        self.log("چرا پیکسوریا", c)

        features = [
            ("zap", "سرعت تحویل بالا", "در چرخه‌های کوتاه تحویل می‌دهیم تا زودتر از همه نتیجه را ببینید.", "wide"),
            ("palette", "هویت بصری متمایز", "طراحی که برند شما را از رقبا متمایز می‌کند.", "small"),
            ("shield-check", "کیفیت تضمین‌شده", "تست روی دستگاه‌ها و مرورگرها قبل از تحویل.", "small"),
            ("code-2", "کد تمیز و مقیاس‌پذیر", "کدی می‌نویسیم که فردا هم قابل توسعه باشد؛ نه فقط امروز کار کند.", "wide"),
            ("users", "شریک کاری، نه پیمانکار", "شفاف می‌گوییم، راهنمایی می‌کنیم و تا رسیدن به نتیجه کنارتان هستیم. تیم خودتان را بزرگ کنید.", "tall"),
            ("rocket", "پشتیبانی بعد از تحویل", "بعد از انتشار هم در کنارتان می‌مانیم.", "small"),
        ]
        added = 0
        for i, (icon, title, desc, size) in enumerate(features):
            if not WhyFeature.objects.filter(title=title).exists():
                WhyFeature.objects.create(
                    icon=icon, title=title, description=desc, size=size, order=i * 10
                )
                added += 1
        if added:
            self.stdout.write(f"  + {added} ویژگی")

    # ── Tech / skills ──
    def seed_tech(self):
        _, c = first_or_create(
            TechSection,
            subtitle="تکنولوژی‌ها و مهارت‌ها",
            title="با ابزارهای درست می‌سازیم",
            description=(
                "تکنولوژی به خودی خود ارزش نیست؛ انتخاب درست آن است. این ابزارها "
                "هستند که پروژهٔ شما را سریع، پایدار و قابل توسعه نگه می‌دارند."
            ),
        )
        self.log("تکنولوژی", c)

        skills = [
            ("طراحی رابط کاربری", "Figma", 95, "ابزار طراحی"),
            ("توسعهٔ فرانت‌اند", "HTML / CSS / Tailwind", 96, "فرانت‌اند"),
            ("توسعهٔ فرانت‌اند", "JavaScript", 92, "فرانت‌اند"),
            ("انیمیشن و تعامل", "GSAP / Three.js", 85, "فرانت‌اند"),
            ("توسعهٔ بک‌اند", "Python / Django", 94, "بک‌اند"),
            ("پایگاه داده", "PostgreSQL", 82, "بک‌اند"),
            ("استقرار و سرور", "Docker / Linux", 78, "بک‌اند"),
        ]
        added = 0
        for i, (category, name, level, _) in enumerate(skills):
            if not TechSkill.objects.filter(name=name).exists():
                TechSkill.objects.create(
                    name=name, level=level, category=category, order=i * 10
                )
                added += 1
        if added:
            self.stdout.write(f"  + {added} مهارت")

    # ── FAQ ──
    def seed_faq(self):
        _, c = first_or_create(
            FaqSection,
            subtitle="سوالات متداول",
            title="هر سوالی دارید، اینجا بپرسید",
            description=(
                "پاسخ پرتکرارترین پرسش‌هایی را که از ما می‌شود اینجا گذاشته‌ایم. "
                "پاسخ دقیق‌تری نیاز داشتید؟ کافی است تماس بگیرید."
            ),
        )
        self.log("سوالات متداول", c)

        items = [
            (
                "مدت زمان انجام یک پروژه چقدر است؟",
                "بستگی به وسعت پروژه دارد. پروژه‌های پکیج پایه معمولاً در ۱۰ روز کاری "
                "تحویل داده می‌شوند و پروژه‌های سازمانی بین ۴ تا ۸ هفته طول می‌کشند. "
                "در جلسهٔ اول و بعد از بررسی دقیق، برآورد زمان را به شما می‌گوییم.",
            ),
            (
                "قیمت پروژه چگونه محاسبه می‌شود؟",
                "قیمت بر اساس وسعت کار، تعداد صفحات، امکانات موردنیاز و زمان تحویل "
                "تعیین می‌شود. پکیج‌های آماده ما قیمت مشخص دارند؛ برای پروژه‌های "
                "سفارشی پس از جلسهٔ مشاوره پیش‌فاکتور شفافی می‌دهیم.",
            ),
            (
                "بعد از تحویل پروژه پشتیبانی دارید؟",
                "بله. همهٔ پروژه‌ها با دورهٔ پشتیبانی رایگان تحویل می‌شوند و بعد از آن "
                "هم بسته‌های پشتیبانی ماهانه داریم. باگ‌های احتمالی را هم بدون "
                "هزینهٔ اضافه برطرف می‌کنیم.",
            ),
            (
                "محتوا و عکس‌های سایت را خودمان آماده می‌کنیم؟",
                "اختیاری است. اگر محتوایی دارید، با آن کار می‌کنیم؛ اگر نه، تیم "
                "تولید محتوای ما می‌تواند متن و تصاویر را برایتان آماده کند.",
            ),
            (
                "قرارداد و نحوهٔ پرداخت چگونه است؟",
                "همکاری با قرارداد رسمی شروع می‌شود. پرداخت معمولاً در سه مرحله است: "
                "بیعانهٔ شروع، عقد مرحلهٔ طراحی و تسویهٔ هنگام تحویل. برای پروژه‌های "
                "طولانی‌تر، اقساط منعطف هم داریم.",
            ),
        ]
        added = 0
        for i, (question, answer) in enumerate(items):
            if not FaqItem.objects.filter(question=question).exists():
                FaqItem.objects.create(
                    question=question, answer=answer, order=i * 10
                )
                added += 1
        if added:
            self.stdout.write(f"  + {added} سوال متداول")

    # ── Contact lead form ──
    def seed_contact(self):
        _, c = first_or_create(
            ContactSection,
            subtitle="فرم تماس سریع",
            title="پروژه‌تان را شروع کنید",
            description=(
                "نام، شماره و یک پیام کوتاه کافی است. در کمتر از ۲۴ ساعت پاسخ "
                "می‌دهیم و در یک جلسهٔ کوتاه، ایده‌تان را بررسی می‌کنیم."
            ),
            submit_text="ارسال درخواست",
            success_text="درخواست شما دریافت شد. به‌زودی با شما تماس می‌گیریم.",
        )
        self.log("فرم تماس", c)

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

    # ── Site settings + socials (only when the table is empty) ──
    def seed_site(self):
        if SiteSettings.objects.exists():
            return
        SiteSettings.objects.create(
            site_name="پیکسوریا",
            site_description="استودیو طراحی و توسعهٔ محصولات دیجیتال",
            footer_description=(
                "پیکسوریا استودیویی مستقل است که به برندها کمک می‌کند تجربهٔ دیجیتال "
                "خود را بهتر بسازند؛ از ایده تا اجرا."
            ),
            email="hello@pixoria.ir",
            phone="۰۵۱-۱۲۳۴۵۶۷۸",
            address="مشهد، ایران",
            established_year="۱۳۹۸",
            status="آماده همکاری",
        )
        self.stdout.write("  + تنظیمات سایت")

        socials = [
            ("IG", "اینستاگرام", "https://instagram.com/pixoria", 10),
            ("LI", "لینکدین", "https://linkedin.com/company/pixoria", 20),
            ("TG", "تلگرام", "https://t.me/pixoria", 30),
        ]
        for label, name, url, order in socials:
            if not SocialLink.objects.filter(url=url).exists():
                SocialLink.objects.create(label=label, name=name, url=url, order=order)
        self.stdout.write("  + شبکه‌های اجتماعی")

    def log(self, name, created):
        if created:
            self.stdout.write(f"  + {name}")
