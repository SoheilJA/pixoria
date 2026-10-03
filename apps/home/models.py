from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class HeroSection(models.Model):
    """هیرو سکشن"""

    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    class Meta:
        verbose_name = "هیرو سکشن"
        verbose_name_plural = "هیرو سکشن"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and HeroSection.objects.exists():
            raise ValueError("فقط یک هیروسکشن مجاز است")
        super().save(*args, **kwargs)


class HeroMarqueeItem(models.Model):
    """آیتم های مارکویی"""

    text = models.CharField(max_length=100, verbose_name="متن")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "آیتم مارکویی اول هیروسکشن"
        verbose_name_plural = "آیتم های مارکویی هیروسکشن"
        ordering = ["order"]

    def __str__(self):
        return self.text


class FeaturedWorkSection(models.Model):
    """سکشن نمونه کار های منتخب"""

    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    class Meta:
        verbose_name = "سکشن نمونه کار"
        verbose_name_plural = "سکشن نمونه کار ها"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and FeaturedWorkSection.objects.exists():
            raise ValueError("فقط یک سکشن نمونه کار مجاز است")
        super().save(*args, **kwargs)


class ServicesSection(models.Model):
    """سکشن خدمات ما در صفحه اصلی"""

    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    class Meta:
        verbose_name = "سکشن خدمات"
        verbose_name_plural = "سکشن خدمات"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and ServicesSection.objects.exists():
            raise ValueError("فقط یک سکشن خدمات مجاز است")
        super().save(*args, **kwargs)


class ClientMarqueeItem(models.Model):
    """آیتم های مارکویی برند های همکار"""

    name = models.CharField(max_length=200, verbose_name="نام برند")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "برند همکار"
        verbose_name_plural = "برند های همکار"
        ordering = ["order"]

    def __str__(self):
        return self.name


class ManifestoSection(models.Model):
    """سکشن برتری های ما"""

    label = models.CharField(max_length=100, verbose_name="ساب تایتل ")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    highlighted_word = models.CharField(max_length=50, verbose_name="کلمه هایلایت شده")
    paragraph_one = models.TextField(verbose_name="پاراگراف اول")
    paragraph_two = models.TextField(verbose_name="پاراگراف دوم")
    signature_name = models.CharField(max_length=100, verbose_name="نام امضا")
    signature_title = models.CharField(max_length=100, verbose_name="عنوان امضا")

    class Meta:
        verbose_name = "سکشن برتری های ما"
        verbose_name_plural = "سکشن برتری های ما"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and ManifestoSection.objects.exists():
            raise ValueError("فقط یک سکشن برتری مجاز است")
        super().save(*args, **kwargs)


class CTASection(models.Model):
    """سکشن کال تو اکشن - ثابت در همه صفحات"""

    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")
    email = models.EmailField(verbose_name="ایمیل")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")

    class Meta:
        verbose_name = "CTA سکشن"
        verbose_name_plural = "CTA سکشن"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and CTASection.objects.exists():
            raise ValueError("فقط یک کال تو اکشن مجاز است")
        super().save(*args, **kwargs)


class LatestArticlesSection(models.Model):
    """سکشن آخرین مقالات در صفحه اصلی"""

    subtitle = models.CharField(max_length=100, verbose_name="ساب تایتل")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    class Meta:
        verbose_name = "سکشن آخرین مقالات"
        verbose_name_plural = "سکشن آخرین مقالات"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and LatestArticlesSection.objects.exists():
            raise ValueError("فقط یک سکشن آخرین مقالات مجاز است")
        super().save(*args, **kwargs)


class HeaderSettings(models.Model):
    """تنظیمات هدر بالای سایت — دکمهٔ CTA"""

    cta_text = models.CharField(max_length=50, verbose_name="متن دکمه CTA", default="شروع پروژه")
    cta_url = models.CharField(
        max_length=200,
        verbose_name="لینک دکمه CTA",
        blank=True,
        help_text="نام آدرس جنگو (مثل contact:contact) یا مسیر مستقیم (مثل /contact/)",
    )
    show_cta = models.BooleanField(default=True, verbose_name="نمایش دکمه CTA")

    class Meta:
        verbose_name = "تنظیمات هدر"
        verbose_name_plural = "تنظیمات هدر"

    def __str__(self):
        return "تنظیمات هدر"

    def save(self, *args, **kwargs):
        if not self.pk and HeaderSettings.objects.exists():
            raise ValueError("فقط یک تنظیمات هدر مجاز است")
        super().save(*args, **kwargs)


class NavItem(models.Model):
    """آیتم‌های منوی بالای سایت"""

    title = models.CharField(max_length=100, verbose_name="عنوان")
    url = models.CharField(
        max_length=200,
        verbose_name="لینک",
        help_text="نام آدرس جنگو (مثل portfolio:list) یا مسیر مستقیم (مثل /blog/)",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "آیتم منو"
        verbose_name_plural = "آیتم‌های منو"
        ordering = ["order"]

    def __str__(self):
        return self.title


class HomeSection(models.Model):
    """ثبت بخش‌های صفحه اصلی — ترتیب و نمایش از همینجا مدیریت می‌شود.

    هر کلید به یک پارشال در templates/home/sections/_<key>.html اشاره دارد.
    بخش‌های هیرو و مقالات هم از همین سیستم عبور می‌کنند تا بدون شکستن
    جریان دادهٔ آنها، قابل مرتب‌سازی باشند."""

    KEY_CHOICES = [
        ("hero", "هیرو"),
        ("clients", "برندهای همکار"),
        ("works", "نمونه‌کارهای منتخب"),
        ("stats", "آمار و ارقام"),
        ("services", "خدمات"),
        ("process", "فرآیند کار"),
        ("why", "چرا پیکسوریا"),
        ("tech", "تکنولوژی‌ها و مهارت‌ها"),
        ("packages", "پکیج‌ها و قیمت‌ها"),
        ("testimonials", "نظرات مشتریان"),
        ("faq", "سوالات متداول"),
        ("contact", "فرم تماس سریع"),
        ("manifesto", "مانیفست برند"),
        ("articles", "آخرین مقالات"),
    ]

    key = models.CharField(
        max_length=30, choices=KEY_CHOICES, unique=True, verbose_name="کلید بخش"
    )
    title = models.CharField(
        max_length=100,
        verbose_name="عنوان (مدیریتی)",
        help_text="فقط برای نمایش در پنل ادمین استفاده می‌شود",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "بخش صفحه اصلی"
        verbose_name_plural = "بخش‌های صفحه اصلی"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class StatsSection(models.Model):
    """تنظیمات بخش آمار و ارقام"""

    subtitle = models.CharField(max_length=100, verbose_name="ساب تایتل")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    class Meta:
        verbose_name = "سکشن آمار"
        verbose_name_plural = "سکشن آمار"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and StatsSection.objects.exists():
            raise ValueError("فقط یک سکشن آمار مجاز است")
        super().save(*args, **kwargs)


class StatItem(models.Model):
    """آیتم آمار — شمارش انیمیشنی"""

    section = models.ForeignKey(
        StatsSection,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سکشن",
        null=True,
        blank=True,
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=1, verbose_name="مقدار", help_text="مثلاً ۱۲۰"
    )
    prefix = models.CharField(max_length=10, verbose_name="پیشوند", blank=True, help_text="مثلاً +")
    suffix = models.CharField(max_length=10, verbose_name="پسوند", blank=True, help_text="مثلاً ٪")
    label = models.CharField(max_length=100, verbose_name="برچسب")
    description = models.CharField(max_length=200, verbose_name="توضیح کوتاه", blank=True)
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "آیتم آمار"
        verbose_name_plural = "آیتم‌های آمار"
        ordering = ["order"]

    def __str__(self):
        return self.label


class ProcessSection(models.Model):
    """تنظیمات بخش فرآیند کار — از ایده تا تحویل"""

    subtitle = models.CharField(max_length=100, verbose_name="ساب تایتل")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    class Meta:
        verbose_name = "سکشن فرآیند"
        verbose_name_plural = "سکشن فرآیند"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and ProcessSection.objects.exists():
            raise ValueError("فقط یک سکشن فرآیند مجاز است")
        super().save(*args, **kwargs)


class ProcessStep(models.Model):
    """مراحل فرآیند کار"""

    section = models.ForeignKey(
        ProcessSection,
        on_delete=models.CASCADE,
        related_name="steps",
        verbose_name="سکشن",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200, verbose_name="عنوان مرحله")
    description = models.TextField(verbose_name="توضیحات")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "مرحله فرآیند"
        verbose_name_plural = "مراحل فرآیند"
        ordering = ["order"]

    def __str__(self):
        return self.title


class WhySection(models.Model):
    """تنظیمات بخش چرا پیکسوریا"""

    subtitle = models.CharField(max_length=100, verbose_name="ساب تایتل")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    class Meta:
        verbose_name = "سکشن چرا پیکسوریا"
        verbose_name_plural = "سکشن چرا پیکسوریا"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and WhySection.objects.exists():
            raise ValueError("فقط یک سکشن چرا پیکسوریا مجاز است")
        super().save(*args, **kwargs)


class WhyFeature(models.Model):
    """کارت ویژگیِ بنتو گرید"""

    section = models.ForeignKey(
        WhySection,
        on_delete=models.CASCADE,
        related_name="features",
        verbose_name="سکشن",
        null=True,
        blank=True,
    )
    icon = models.CharField(
        max_length=64,
        default="sparkles",
        verbose_name="آیکون",
        help_text=(
            "نام انگلیسی یک آیکون Lucide. مثال: zap، palette، shield-check. "
            "لیست کامل: lucide.dev/icons"
        ),
    )
    title = models.CharField(max_length=100, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")
    size = models.CharField(
        max_length=10,
        choices=[("small", "کوچک"), ("wide", "عریض"), ("tall", "بلند")],
        default="small",
        verbose_name="اندازه کارت",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "ویژگی"
        verbose_name_plural = "ویژگی‌ها"
        ordering = ["order"]

    def __str__(self):
        return self.title


class TechSection(models.Model):
    """تنظیمات بخش تکنولوژی‌ها و مهارت‌ها"""

    subtitle = models.CharField(max_length=100, verbose_name="ساب تایتل")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    class Meta:
        verbose_name = "سکشن تکنولوژی"
        verbose_name_plural = "سکشن تکنولوژی"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and TechSection.objects.exists():
            raise ValueError("فقط یک سکشن تکنولوژی مجاز است")
        super().save(*args, **kwargs)


class TechSkill(models.Model):
    """هر تکنولوژی با نوار پیشرفت"""

    section = models.ForeignKey(
        TechSection,
        on_delete=models.CASCADE,
        related_name="skills",
        verbose_name="سکشن",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100, verbose_name="نام تکنولوژی")
    level = models.PositiveIntegerField(
        default=80, verbose_name="سطح تسلط (٪)", validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    category = models.CharField(max_length=100, verbose_name="دسته‌بندی", blank=True)
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "مهارت"
        verbose_name_plural = "مهارت‌ها"
        ordering = ["order"]

    def __str__(self):
        return self.name


class PackagesSection(models.Model):
    """تنظیمات بخش پکیج‌ها و قیمت‌ها"""

    subtitle = models.CharField(max_length=100, verbose_name="ساب تایتل")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")
    note = models.CharField(
        max_length=200,
        verbose_name="یادداشت پایین",
        blank=True,
        help_text="مثلاً: قیمت‌ها به تومان است و برای پروژه‌های سفارشی متفاوت است",
    )

    class Meta:
        verbose_name = "سکشن پکیج‌ها"
        verbose_name_plural = "سکشن پکیج‌ها"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and PackagesSection.objects.exists():
            raise ValueError("فقط یک سکشن پکیج‌ها مجاز است")
        super().save(*args, **kwargs)


class Package(models.Model):
    """یک پکیج قیمت‌گذاری"""

    section = models.ForeignKey(
        PackagesSection,
        on_delete=models.CASCADE,
        related_name="packages",
        verbose_name="سکشن",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100, verbose_name="نام پکیج")
    description = models.CharField(max_length=200, verbose_name="توضیح کوتاه", blank=True)
    price = models.CharField(
        max_length=100,
        verbose_name="قیمت",
        blank=True,
        help_text="مثلاً ۱۲٬۰۰۰٬۰۰۰. خالی بگذارید تا «استعلام قیمت» نمایش داده شود",
    )
    price_note = models.CharField(
        max_length=100, verbose_name="یادداشت قیمت", blank=True, help_text="مثلاً ماهانه یا هر پروژه"
    )
    is_featured = models.BooleanField(default=False, verbose_name="پکیج پیشنهادی")
    badge = models.CharField(max_length=50, verbose_name="نشان پکیج", blank=True, help_text="مثلاً پرطرفدار")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "پکیج"
        verbose_name_plural = "پکیج‌ها"
        ordering = ["order"]

    def __str__(self):
        return self.name


class PackageFeature(models.Model):
    """ویژگی‌های هر پکیج"""

    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="features",
        verbose_name="پکیج",
    )
    title = models.CharField(max_length=200, verbose_name="عنوان ویژگی")
    included = models.BooleanField(default=True, verbose_name="شامل می‌شود")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "ویژگی پکیج"
        verbose_name_plural = "ویژگی‌های پکیج"
        ordering = ["order"]

    def __str__(self):
        return self.title


class FaqSection(models.Model):
    """تنظیمات بخش سوالات متداول"""

    subtitle = models.CharField(max_length=100, verbose_name="ساب تایتل")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    class Meta:
        verbose_name = "سکشن سوالات متداول"
        verbose_name_plural = "سکشن سوالات متداول"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and FaqSection.objects.exists():
            raise ValueError("فقط یک سکشن سوالات متداول مجاز است")
        super().save(*args, **kwargs)


class FaqItem(models.Model):
    """یک سوال و جواب"""

    section = models.ForeignKey(
        FaqSection,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سکشن",
        null=True,
        blank=True,
    )
    question = models.CharField(max_length=300, verbose_name="سوال")
    answer = models.TextField(verbose_name="جواب")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "سوال متداول"
        verbose_name_plural = "سوالات متداول"
        ordering = ["order"]

    def __str__(self):
        return self.question


class ContactSection(models.Model):
    """تنظیمات بخش فرم تماس سریع در صفحه اصلی"""

    subtitle = models.CharField(max_length=100, verbose_name="ساب تایتل")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")
    submit_text = models.CharField(max_length=50, verbose_name="متن دکمه ارسال", default="ارسال درخواست")
    success_text = models.CharField(
        max_length=200, verbose_name="پیام موفقیت", default="درخواست شما دریافت شد. به‌زودی تماس می‌گیریم."
    )

    class Meta:
        verbose_name = "سکشن فرم تماس"
        verbose_name_plural = "سکشن فرم تماس"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and ContactSection.objects.exists():
            raise ValueError("فقط یک سکشن فرم تماس مجاز است")
        super().save(*args, **kwargs)
