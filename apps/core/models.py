from django.db import models

from .icon_utils import validate_icon_name


class SiteSettings(models.Model):
    """تنظیمات کلی سایت"""

    site_name = models.CharField(max_length=100, verbose_name="نام سایت")
    site_description = models.TextField(verbose_name="توضیحات سایت")
    footer_description = models.TextField(verbose_name="توضیحات فوتر")
    email = models.EmailField(verbose_name="ایمیل")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")
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

    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

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

    description = models.TextField(verbose_name="توضیحات ")

    class Meta:
        verbose_name = "داستان ما"
        verbose_name_plural = "داستان ما"

    def __str__(self):
        return "داستان ما"

    def save(self, *args, **kwargs):
        if not self.pk and AboutStory.objects.exists():
            raise ValueError("فقط یک سکشن مجاز است")
        super().save(*args, **kwargs)


class TeamMember(models.Model):
    """اعضای تیم"""

    name = models.CharField(max_length=100, verbose_name="نام")
    role = models.TextField(verbose_name="نقش")
    bio = models.TextField(verbose_name="توضیحات")
    image = models.ImageField(upload_to="team/", verbose_name="تصویر")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "عضو تیم"
        verbose_name_plural = "اعضای تیم"
        ordering = ["order"]

    def __str__(self):
        return self.name


class AboutValue(models.Model):
    """ارزش های سئو ران"""

    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "ارزش"
        verbose_name_plural = "ارزش ها"
        ordering = ["order"]

    def __str__(self):
        return self.title


class AboutStat(models.Model):
    """آمار و ارقام"""

    number = models.CharField(max_length=50, verbose_name="عدد", help_text="مثلا +70")
    label = models.CharField(max_length=100, verbose_name="برچست")
    description = models.CharField(
        max_length=200, verbose_name="توضیحات کوتاه", blank=True
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "آمار"
        verbose_name_plural = "امار و ارقام"
        ordering = ["order"]

    def __str__(self):
        return self.label


class AboutPre(models.Model):
    """پریفوتر درباره ما"""

    label = models.CharField(max_length=100, verbose_name="ساب تایتل")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")
    button_text = models.CharField(max_length=100, verbose_name="متن دکمه")
    button_url = models.CharField(max_length=200, verbose_name="لینک دکمه")

    class Meta:
        verbose_name = "سکشن پریفوتر درباه ما"
        verbose_name_plural = "سکشن پریفوتر درباره ما"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and AboutPre.objects.exists():
            raise ValueError("فقط یک سکشن مجاز است")
        super().save(*args, **kwargs)


class AboutMission(models.Model):
    """ماموریت و چشم‌انداز — تک‌سکشن"""

    label = models.CharField(max_length=100, verbose_name="ساب تایتل", default="ماموریت ما")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")
    image = models.ImageField(
        upload_to="about/mission/", verbose_name="تصویر", blank=True, null=True
    )

    class Meta:
        verbose_name = "ماموریت ما"
        verbose_name_plural = "ماموریت ما"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and AboutMission.objects.exists():
            raise ValueError("فقط یک سکشن مجاز است")
        super().save(*args, **kwargs)


class AboutProcessStep(models.Model):
    """مراحل همکاری"""

    title = models.CharField(max_length=200, verbose_name="عنوان مرحله")
    description = models.TextField(verbose_name="توضیحات")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "مرحله همکاری"
        verbose_name_plural = "مراحل همکاری"
        ordering = ["order"]

    def __str__(self):
        return self.title


class AboutFaq(models.Model):
    """سوالات متداول درباره ما"""

    question = models.CharField(max_length=300, verbose_name="سوال")
    answer = models.TextField(verbose_name="پاسخ")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "سوال متداول"
        verbose_name_plural = "سوالات متداول"
        ordering = ["order"]

    def __str__(self):
        return self.question


"""مدل های پروپوزال"""


class Proposal(models.Model):
    """پروپوزال برای مشتری"""

    # اطلاعات اصلی
    client_name = models.CharField(max_length=200, verbose_name="نام مشتری")
    client_website = models.URLField(verbose_name="آدرس سایت مشتری")
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name="اسلاگ", help_text="مثلاً: digikala"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # تصاویر
    website_screenshot = models.ImageField(
        upload_to="proposals/screenshots/", verbose_name="اسکرین‌شات سایت", blank=True
    )
    lighthouse_screenshot = models.ImageField(
        upload_to="proposals/lighthouse/", verbose_name="تصویر Lighthouse", blank=True
    )
    inspect_screenshot = models.ImageField(
        upload_to="proposals/inspect/", verbose_name="تصویر اینسپکت", blank=True
    )

    # معرفی
    intro_title = models.CharField(max_length=200, verbose_name="عنوان معرفی")
    intro_text = models.TextField(verbose_name="متن معرفی")

    # قیمت
    price = models.CharField(
        max_length=100,
        verbose_name="قیمت پیشنهادی",
        blank=True,
        help_text="مثلاً: از ۵ میلیون تومان",
    )

    class Meta:
        verbose_name = "پروپوزال"
        verbose_name_plural = "پروپوزال‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return self.client_name


class ProposalStat(models.Model):
    """آمار و اعداد پروپوزال"""

    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name="stats",
        verbose_name="پروپوزال",
    )
    label = models.CharField(
        max_length=100, verbose_name="برچسب", help_text="مثلاً: امتیاز سرعت فعلی"
    )
    current_value = models.CharField(
        max_length=50, verbose_name="مقدار فعلی", help_text="مثلاً: ۳۲"
    )
    target_value = models.CharField(
        max_length=50, verbose_name="مقدار هدف", help_text="مثلاً: ۹۰+"
    )
    unit = models.CharField(
        max_length=20,
        verbose_name="واحد",
        blank=True,
        help_text="مثلاً: امتیاز یا ثانیه یا ٪",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "آمار"
        verbose_name_plural = "آمارها"
        ordering = ["order"]

    def __str__(self):
        return self.label


class ProposalProblem(models.Model):
    """مشکلات سایت"""

    SEVERITY_CHOICES = [
        ("critical", "بحرانی"),
        ("warning", "متوسط"),
        ("info", "جزئی"),
    ]
    CATEGORY_CHOICES = [
        ("seo", "سئو فنی"),
        ("speed", "سرعت"),
        ("content", "محتوا"),
        ("security", "امنیت"),
        ("ux", "تجربه کاربری"),
        ("other", "سایر"),
    ]
    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name="problems",
        verbose_name="پروپوزال",
    )
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, verbose_name="دسته‌بندی"
    )
    severity = models.CharField(
        max_length=10, choices=SEVERITY_CHOICES, verbose_name="شدت"
    )
    title = models.CharField(max_length=200, verbose_name="عنوان مشکل")
    description = models.TextField(verbose_name="توضیح مشکل", blank=True)
    solution = models.TextField(verbose_name="راه‌حل پیشنهادی", blank=True)
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "مشکل"
        verbose_name_plural = "مشکلات"
        ordering = ["order"]

    def __str__(self):
        return self.title


class ProposalService(models.Model):
    """خدمات پیشنهادی"""

    TYPE_CHOICES = [
        ("essential", "ضروری"),
        ("optional", "اختیاری"),
    ]
    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name="پروپوزال",
    )
    title = models.CharField(max_length=200, verbose_name="عنوان خدمت")
    description = models.TextField(verbose_name="توضیحات", blank=True)
    service_type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default="essential", verbose_name="نوع"
    )
    price = models.CharField(max_length=100, verbose_name="قیمت", blank=True)
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "خدمت پیشنهادی"
        verbose_name_plural = "خدمات پیشنهادی"
        ordering = ["order"]

    def __str__(self):
        return self.title
