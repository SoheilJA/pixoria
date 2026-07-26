from django.db import models


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

    url = models.URLField(verbose_name="لینک")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "شبکه اجتماعی"
        verbose_name_plural = "شبکه‌های اجتماعی"
        ordering = ["order"]

    def __str__(self):
        return self.label


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
