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
)


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
