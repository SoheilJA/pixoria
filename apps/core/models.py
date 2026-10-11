from django.db import models

from .brand_utils import brand_choices, default_brand_option
from .icon_utils import validate_icon_name

# راهنمای مشترک فیلد آیکون — در چندین مدل تکرار می‌شود تا متن کمکی یکسانی داشته
# باشد. آیکون‌ها از اسپرایت محلی لوساید بارگذاری می‌شوند (بدون CDN).
ICON_HELP = (
    "نام انگلیسی یک آیکون Lucide، بدون فاصله. "
    "مثال: zap، palette، shield-check. "
    "لیست کامل آیکون‌ها: lucide.dev/icons"
)
# راهنمای مشترک فیلد متن بالای عنوان (eyebrow) که در سکشن‌های v2 بالای عنوان
# می‌آید.
EYEBROW_HELP = "متن کوچک و طلاییِ بالای عنوان. مثلاً: داستان ما"
# راهنمای مشترک فیلد عنوان سکشن‌ها — مارکر [[ ]] کلمهٔ رنگی را مشخص می‌کند.
TITLE_HELP = "کلمه‌ای که باید رنگی شود را داخل [[ ]] بنویسید."
# راهنمای مشترک فیلدهای لینک دکمه‌ها — نام آدرس جنگو، مسیر مستقیم یا لنگر.
URL_HELP = (
    "نام آدرس جنگو (مثل contact:contact)، مسیر مستقیم (مثل /blog/) "
    "یا لنگر صفحه (مثل #contact)"
)


class SiteSettings(models.Model):
    """تنظیمات کلی سایت"""

    site_name = models.CharField(max_length=100, verbose_name="نام سایت")
    site_description = models.TextField(verbose_name="توضیحات سایت")
    footer_description = models.TextField(verbose_name="توضیحات فوتر")
    email = models.EmailField(verbose_name="ایمیل")
    phone = models.CharField(
        max_length=20,
        verbose_name="شماره تماس",
        help_text="شماره اصلی. در هدر، فوتر، CTA و کارت‌های صفحهٔ تماس نمایش داده می‌شود.",
    )
    phone_label = models.CharField(
        max_length=50,
        verbose_name="برچسب شماره تماس",
        blank=True,
        default="دفتر مرکزی",
        help_text=(
            "برچسب کوچک بالای شمارهٔ اصلی در کارت‌های صفحهٔ تماس و فوتر. "
            "خالی بگذارید تا برچسبی نمایش داده نشود."
        ),
    )
    address = models.TextField(verbose_name="آدرس", blank=True)
    established_year = models.CharField(max_length=10, verbose_name="سال تاسیس")
    status = models.CharField(
        max_length=50, verbose_name="وضعیت", default="آماده همکاری"
    )

    # ── بخش برند فوتر ──
    tagline = models.CharField(
        max_length=200,
        verbose_name="شعار برند",
        blank=True,
        help_text="مثلاً: هویتی درخشان، اعتباری ماندگار.",
    )
    phone_secondary = models.CharField(
        max_length=20,
        verbose_name="شماره همراه",
        blank=True,
        help_text="شماره دوم نمایش‌داده‌شده در فوتر و منوی موبایل",
    )
    phone_secondary_label = models.CharField(
        max_length=50,
        verbose_name="برچسب شماره همراه",
        blank=True,
        default="پشتیبانی",
        help_text=(
            "برچسب کوچک بالای شمارهٔ دوم در کارت‌های صفحهٔ تماس و فوتر. "
            "خالی بگذارید تا برچسبی نمایش داده نشود."
        ),
    )
    website = models.URLField(
        verbose_name="آدرس وب‌سایت", blank=True, help_text="مثلاً: https://www.pixoria.ir"
    )
    og_image = models.FileField(
        verbose_name="تصویر اشتراک‌گذاری (OG)",
        upload_to="brand/",
        blank=True,
        help_text="تصویر پیش‌نمایش شبکه‌های اجتماعی (۱۲۰۰×۶۳۰ پیکسل توصیه می‌شود)",
    )

    # ── کارت‌های اعتماد و امنیت در فوتر ──
    trust_first_title = models.CharField(
        max_length=50, verbose_name="عنوان کارت اول اعتماد", blank=True, default="اینماد"
    )
    trust_first_subtitle = models.CharField(
        max_length=100,
        verbose_name="زیرنویس کارت اول",
        blank=True,
        default="درگاه امن پرداخت",
    )
    trust_second_title = models.CharField(
        max_length=50,
        verbose_name="عنوان کارت دوم اعتماد",
        blank=True,
        default="ساماندهی",
    )
    trust_second_subtitle = models.CharField(
        max_length=100,
        verbose_name="زیرنویس کارت دوم",
        blank=True,
        default="ثبت رسمی کسب‌وکار",
    )
    trust_note = models.CharField(
        max_length=300,
        verbose_name="یادداشت بخش اعتماد",
        blank=True,
        default="لوگوی اینماد و ساماندهی پس از دریافت در همین قسمت قرار می‌گیرد.",
    )

    # ─ـ مگامنوی خدمات در هدر ──
    mega_title = models.CharField(
        max_length=200,
        verbose_name="عنوان بنر مگامنو",
        blank=True,
        help_text=(
            "عنوان بنر بالای منوی کشویی خدمات در هدر. "
            "کلمه‌ای که باید رنگی شود را داخل [[ ]] بنویسید. "
            "مثلاً: چهار سرویس حرفه‌ای، یک [[برند ماندگار]]"
        ),
    )
    mega_description = models.CharField(
        max_length=300,
        verbose_name="توضیح بنر مگامنو",
        blank=True,
        help_text="توضیح کوتاه زیر عنوان بنر مگامنو (اختیاری).",
    )
    mega_cta_text = models.CharField(
        max_length=50,
        verbose_name="متن دکمهٔ بنر مگامنو",
        blank=True,
        default="مشاهده همه خدمات",
        help_text=(
            "متن دکمهٔ انتهای بنر مگامنو؛ این دکمه به صفحهٔ همه خدمات لینک می‌شود."
        ),
    )

    logo = models.FileField(
        verbose_name="لوگوی سایت",
        upload_to="brand/",
        blank=True,
        help_text=(
            "فایل لوگوی دلخواه (SVG یا PNG با پس‌زمینه شفاف). "
            "در صورت خالی گذاشتن، وردمارک پیکسلی «پیکسوریا» نمایش داده می‌شود."
        ),
    )
    favicon = models.FileField(
        verbose_name="فاوآیکون",
        upload_to="brand/",
        blank=True,
        help_text=(
            "فاوآیکون دلخواه (حداقل ۴۸×۴۸ پیکسل). "
            "در صورت خالی گذاشتن، فاوآیکون پیش‌فرضِ وردمارک پیکسلی استفاده می‌شود."
        ),
    )
    apple_touch_icon = models.FileField(
        verbose_name="آیکون صفحهٔ اصلی iOS",
        upload_to="brand/",
        blank=True,
        help_text=(
            "آیکون ۱۸۰×۱۸۰ پیکسل برای Home Screen در iOS. "
            "در صورت خالی گذاشتن، آیکون پیش‌فرض استفاده می‌شود."
        ),
    )
    logo_choice = models.CharField(
        max_length=64,
        blank=True,
        default=default_brand_option,
        choices=brand_choices,
        verbose_name="مجموعهٔ لوگوی پیش‌فرض",
        help_text=(
            "یکی از مفاهیم آمادهٔ لوگوی فضایی (در static/brand/). "
            "این گزینه فقط تا زمانی که فایل لوگوی دلخواه آپلود نشده استفاده می‌شود. "
            "خالی یا نامعتبر = گزینهٔ اول."
        ),
    )
    favicon_choice = models.CharField(
        max_length=64,
        blank=True,
        default=default_brand_option,
        verbose_name="مجموعهٔ فاوآیکون پیش‌فرض",
        help_text=(
            "مجموعهٔ فاوآیکون و آیکون‌های PWA. اگر خالی باشد، از همان گزینهٔ لوگو "
            "استفاده می‌شود. فاوآیکون آپلودشده اولویت دارد."
        ),
    )

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError("فقط یک تنظیمات سایت مجاز است")
        super().save(*args, **kwargs)


class SocialLink(models.Model):
    """لینک های شبکه های اجتماعی"""

    label = models.CharField(
        max_length=10, verbose_name="برچست", help_text="مثلا LI یا IG"
    )
    name = models.CharField(
        max_length=50, verbose_name="نام کامل", help_text="مثلا اینستاگرام"
    )
    icon = models.CharField(
        max_length=64,
        verbose_name="آیکون",
        blank=True,
        default="globe",
        validators=[validate_icon_name],
        help_text=(
            "نام انگلیسی یک آیکون Lucide. مثال: instagram، linkedin، send (تلگرام)، "
            "globe. لیست کامل: lucide.dev/icons"
        ),
    )

    url = models.URLField(verbose_name="لینک")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "شبکه اجتماعی"
        verbose_name_plural = "شبکه‌های اجتماعی"
        ordering = ["order"]

    def __str__(self):
        return self.label


class FooterLinkGroup(models.Model):
    """ستون لینک‌های فوتر — مثلاً «دسترسی سریع» یا группы دلخواه"""

    title = models.CharField(max_length=100, verbose_name="عنوان ستون")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "ستون لینک‌های فوتر"
        verbose_name_plural = "ستون‌های لینک‌های فوتر"
        ordering = ["order"]

    def __str__(self):
        return self.title


class FooterLink(models.Model):
    """آیتم لینک داخل یک ستون فوتر"""

    group = models.ForeignKey(
        FooterLinkGroup,
        on_delete=models.CASCADE,
        related_name="links",
        verbose_name="ستون",
    )
    title = models.CharField(max_length=100, verbose_name="عنوان")
    url = models.CharField(
        max_length=200,
        verbose_name="لینک",
        help_text="نام آدرس جنگو (مثل portfolio:list) یا مسیر مستقیم (مثل /blog/)",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "لینک فوتر"
        verbose_name_plural = "لینک‌های فوتر"
        ordering = ["order"]

    def __str__(self):
        return self.title


"""مدل های صفحه درباره ما"""


class AboutPageHero(models.Model):
    """هیرو سکشن درباره ما"""

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        help_text=TITLE_HELP + " مثال: داستانی که از [[۱۳۸۹]] آغاز شد",
    )
    description = models.TextField(verbose_name="توضیحات")
    eyebrow = models.CharField(
        max_length=200,
        verbose_name="متن بالای عنوان",
        blank=True,
        help_text=EYEBROW_HELP + ". مثال: استودیوی طراحی و توسعهٔ پیکسوریا",
    )
    cta_primary_text = models.CharField(
        max_length=50, verbose_name="متن دکمهٔ اصلی", default="تماس با ما"
    )
    cta_primary_url = models.CharField(
        max_length=200, verbose_name="لینک دکمهٔ اصلی", default="contact:contact",
        help_text=URL_HELP,
    )
    cta_secondary_text = models.CharField(
        max_length=50, verbose_name="متن دکمهٔ دوم", default="خدمات ما"
    )
    cta_secondary_url = models.CharField(
        max_length=200,
        verbose_name="لینک دکمهٔ دوم",
        blank=True,
        default="services:list",
        help_text=URL_HELP + ". خالی بگذارید تا دکمهٔ دوم نمایش داده نشود",
    )

    class Meta:
        verbose_name = "هیروسکشن صفحه درباره ما"
        verbose_name_plural = "هیروسکشن صفحه درباره ما"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and AboutPageHero.objects.exists():
            raise ValueError("فقط یک هیرو مجاز است")
        super().save(*args, **kwargs)


class AboutStory(models.Model):
    """داستان ما"""

    description = models.TextField(
        verbose_name="پاراگراف اصلی",
        help_text="اولین و بزرگ‌ترین پاراگرافِ بخش داستان (روشن).",
    )
    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        blank=True,
        help_text=TITLE_HELP + " مثال: از یک استودیوی طراحی، تا مشاورِ [[برندها]]",
    )
    body = models.TextField(
        verbose_name="پاراگراف‌های تکمیلی",
        blank=True,
        help_text="پاراگراف‌های بعدیِ داستان — هر خط یک پاراگراف جداگانه.",
    )
    chips = models.CharField(
        max_length=300,
        verbose_name="برچسب‌ها",
        blank=True,
        help_text="متن‌های کوچکِ کپسولی زیر داستان، جدا شده با ویرگول. مثلاً: مشهد، شرکت‌ها و ادارات",
    )
    quote = models.TextField(
        verbose_name="نقل‌قول",
        blank=True,
        help_text="نقل‌قولِ انتهای بخش داستان. خالی بگذارید تا نقل‌قول نمایش داده نشود.",
    )
    image = models.ImageField(
        upload_to="about/story/",
        verbose_name="تصویر",
        blank=True,
        null=True,
        help_text="تصویر کنار داستان (نسبت ۴:۳). اختیاری.",
    )
    image_alt = models.CharField(
        max_length=200, verbose_name="متن جایگزین تصویر", blank=True
    )
    image_caption = models.CharField(
        max_length=100,
        verbose_name="کپشن تصویر",
        blank=True,
        help_text="متن داخل کپسولِ روی تصویر. مثلاً: مشهد",
    )

    def get_chips_list(self):
        """لیست برچسب‌ها — فیلد csv را به لیست پایتون تبدیل می‌کند."""
        return [chip.strip() for chip in self.chips.split(",") if chip.strip()]

    class Meta:
        verbose_name = "داستان ما"
        verbose_name_plural = "داستان ما"

    def __str__(self):
        return "داستان ما"

    def save(self, *args, **kwargs):
        if not self.pk and AboutStory.objects.exists():
            raise ValueError("فقط یک سکشن مجاز است")
        super().save(*args, **kwargs)


class AboutJourneySection(models.Model):
    """بخش «مسیر» — جدول زمانی حوزه‌های فعالیت (روشن → تیره)"""

    eyebrow = models.CharField(
        max_length=100,
        verbose_name="متن بالای عنوان",
        blank=True,
        default="حوزه‌های فعالیت",
        help_text=EYEBROW_HELP,
    )
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        default="حوزه‌ها، در یک [[مسیر]]",
        help_text=TITLE_HELP,
    )
    subtitle = models.CharField(
        max_length=300, verbose_name="توضیح کوتاه", blank=True
    )
    badge_icon = models.CharField(
        max_length=64,
        verbose_name="آیکون کپسول",
        default="award",
        validators=[validate_icon_name],
        help_text="آیکون کپسول شناورِ روی نقشهٔ مسیر. " + ICON_HELP,
    )
    badge_text = models.CharField(
        max_length=100,
        verbose_name="متن کپسول",
        blank=True,
        default="+۱۵ سال تجربه",
        help_text="متن کپسول شناورِ روی نقشهٔ مسیر. اعداد فارسی نمایش داده می‌شوند.",
    )

    class Meta:
        verbose_name = "بخش مسیر صفحه درباره ما"
        verbose_name_plural = "بخش مسیر صفحه درباره ما"

    def __str__(self):
        return "بخش مسیر"

    def save(self, *args, **kwargs):
        if not self.pk and AboutJourneySection.objects.exists():
            raise ValueError("فقط یک سکشن مجاز است")
        super().save(*args, **kwargs)


class AboutJourneyStep(models.Model):
    """یک ایستگاه از مسیرِ حوزه‌های فعالیت"""

    year = models.CharField(
        max_length=20,
        verbose_name="سال یا عنوان",
        blank=True,
        help_text="مثلاً ۱۳۸۹ برای ایستگاه اول، یا «امروز» برای ایستگاه آخر.",
    )
    title = models.CharField(max_length=200, verbose_name="عنوان ایستگاه")
    subtitle = models.CharField(
        max_length=200, verbose_name="توضیح کوتاه", blank=True
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "ایستگاه مسیر"
        verbose_name_plural = "ایستگاه‌های مسیر"
        ordering = ["order"]

    def __str__(self):
        return self.title


class AboutStat(models.Model):
    """آمار و ارقام"""

    number = models.CharField(
        max_length=50,
        verbose_name="متن عدد (قدیمی)",
        blank=True,
        help_text="فیلد قدیمیِ نمایش عدد. در طرح v2 از «مقدار»، «پیشوند» و «پسوند» استفاده می‌شود.",
    )
    value = models.PositiveIntegerField(
        default=0,
        verbose_name="مقدار",
        help_text="عدد شمارش‌شوندهٔ انیمیشنی. مثلاً ۱۵۰",
    )
    prefix = models.CharField(
        max_length=10,
        verbose_name="پیشوند",
        blank=True,
        help_text="مثلاً +",
    )
    suffix = models.CharField(
        max_length=10,
        verbose_name="پسوند",
        blank=True,
        help_text="مثلاً ٪",
    )
    label = models.CharField(max_length=100, verbose_name="برچست")
    description = models.CharField(
        max_length=200, verbose_name="توضیحات کوتاه", blank=True
    )
    icon = models.CharField(
        max_length=64,
        blank=True,
        default="award",
        verbose_name="آیکون",
        help_text=ICON_HELP,
        validators=[validate_icon_name],
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "آمار"
        verbose_name_plural = "امار و ارقام"
        ordering = ["order"]

    def __str__(self):
        return self.label


class AboutClientsSection(models.Model):
    """بخش «اعتماد مشتریان» — دیوار نام برندهای همکار"""

    eyebrow = models.CharField(
        max_length=100,
        verbose_name="متن بالای عنوان",
        blank=True,
        default="رزومه و اعتماد",
        help_text=EYEBROW_HELP,
    )
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        default="اعتمادِ آن‌ها، [[افتخارِ ما]]",
        help_text=TITLE_HELP,
    )
    subtitle = models.CharField(
        max_length=300, verbose_name="توضیح کوتاه", blank=True
    )

    class Meta:
        verbose_name = "بخش مشتریان صفحه درباره ما"
        verbose_name_plural = "بخش مشتریان صفحه درباره ما"

    def __str__(self):
        return "بخش مشتریان"

    def save(self, *args, **kwargs):
        if not self.pk and AboutClientsSection.objects.exists():
            raise ValueError("فقط یک سکشن مجاز است")
        super().save(*args, **kwargs)
