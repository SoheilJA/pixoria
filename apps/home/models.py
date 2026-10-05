from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.icon_utils import validate_icon_name

# راهنمای مشترک فیلد آیکون — در چندین مدل تکرار می‌شود تا متن کمکی یکسانی داشته
# باشد. آیکون‌ها از اسپرایت محلی لوساید بارگذاری می‌شوند (بدون CDN).
ICON_HELP = (
    "نام انگلیسی یک آیکون Lucide، بدون فاصله. "
    "مثال: zap، palette، shield-check. "
    "لیست کامل آیکون‌ها: lucide.dev/icons"
)
# راهنمای مشترک فیلد متن بالای عنوان (eyebrow) که در سکشن‌های v2 بالای عنوان
# می‌آید.
EYEBROW_HELP = "متن کوچک و طلاییِ بالای عنوان. مثلاً: خدمات ما"
# راهنمای مشترک فیلد عنوان سکشن‌ها — مارکر [[ ]] کلمهٔ رنگی را مشخص می‌کند.
TITLE_HELP = "کلمه‌ای که باید رنگی شود را داخل [[ ]] بنویسید."


class HomeLead(models.Model):
    """درخواست تماس سریعِ فرم صفحه اصلی.

    کوتاه و ساده نگه داشته شده تا از فرم کامل صفحه تماس (ContactSubmission)
    مستقل بماند؛ آن فرنچایز دارای فیلدهای اجباری نوع پروژه و بودجه است که برای
    یک فرم کوچک مناسب نیست."""

    STATUS_CHOICES = [("new", "جدید"), ("seen", "مشاهده شده")]

    name = models.CharField(max_length=200, verbose_name="نام و نام خانوادگی")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="home_leads",
        verbose_name="خدمت موردنظر",
    )
    message = models.TextField(verbose_name="پیام", blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="new", verbose_name="وضعیت"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")

    class Meta:
        verbose_name = "درخواست تماس سریع"
        verbose_name_plural = "درخواست‌های تماس سریع"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.created_at:%Y/%m/%d}"


class HeroSection(models.Model):
    """هیرو سکشن — نسخهٔ v2 با صحنهٔ سه‌بعدی و دکمه‌های CTA"""

    eyebrow = models.CharField(
        max_length=200,
        verbose_name="متن بالای عنوان",
        blank=True,
        help_text=EYEBROW_HELP + ". مثال: استودیوی طراحی و توسعه · از سال ۱۳۸۹",
    )
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        help_text=TITLE_HELP + " مثال: تصویری حرفه‌ای، [[برندی ماندگار]]",
    )
    description = models.TextField(verbose_name="توضیحات")
    cta_primary_text = models.CharField(
        max_length=50, verbose_name="متن دکمهٔ اصلی", default="مشاوره رایگان"
    )
    cta_primary_url = models.CharField(
        max_length=200,
        verbose_name="لینک دکمهٔ اصلی",
        default="#contact",
        help_text=(
            "نام آدرس جنگو (مثل contact:contact)، مسیر مستقیم (مثل /blog/) "
            "یا لنگر صفحه (مثل #contact)"
        ),
    )
    cta_secondary_text = models.CharField(
        max_length=50, verbose_name="متن دکمهٔ دوم", default="مشاهده نمونه‌کارها"
    )
    cta_secondary_url = models.CharField(
        max_length=200,
        verbose_name="لینک دکمهٔ دوم",
        blank=True,
        default="#portfolio",
        help_text=(
            "نام آدرس جنگو، مسیر مستقیم یا لنگر صفحه. "
            "خالی بگذارید تا دکمهٔ دوم نمایش داده نشود"
        ),
    )

    class Meta:
        verbose_name = "هیرو سکشن"
        verbose_name_plural = "هیرو سکشن"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and HeroSection.objects.exists():
            raise ValueError("فقط یک هیروسکشن مجاز است")
        super().save(*args, **kwargs)


class HeroStat(models.Model):
    """آمار کوتاهِ زیر دکمه‌های هیرو — مثل «+۵۰۰ کسب‌وکار مشاوره‌شده»"""

    section = models.ForeignKey(
        HeroSection,
        on_delete=models.CASCADE,
        related_name="stats",
        verbose_name="هیرو",
        null=True,
        blank=True,
    )
    value = models.CharField(
        max_length=50,
        verbose_name="مقدار",
        help_text="مثلاً +۵۰۰ یا ۱۳۵+ یا مشهد",
    )
    label = models.CharField(max_length=100, verbose_name="برچسب", blank=True)
    icon = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="آیکون",
        help_text="اختیاری. مثال: map-pin. " + ICON_HELP,
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "آمار هیرو"
        verbose_name_plural = "آمارهای هیرو"
        ordering = ["order"]

    def __str__(self):
        return f"{self.value} — {self.label}"


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


class HomeAboutSection(models.Model):
    """بخش «درباره پیکسوریا» در صفحه اصلی — معرفی کوتاه و شمارنده‌ها"""

    eyebrow = models.CharField(
        max_length=100,
        verbose_name="متن بالای عنوان",
        blank=True,
        default="درباره پیکسوریا",
        help_text=EYEBROW_HELP,
    )
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        help_text=TITLE_HELP + " مثال: پانزده سال تجربه، یک هدف: [[برندی ماندگار]]",
    )
    paragraph_one = models.TextField(verbose_name="پاراگراف اول")
    paragraph_two = models.TextField(verbose_name="پاراگراف دوم", blank=True)
    chips = models.CharField(
        max_length=500,
        verbose_name="برچسب‌ها",
        blank=True,
        help_text="با ویرگول جدا کنید. مثلاً: طراحی سایت، برنامه‌نویسی، خدمات گرافیکی",
    )
    footer_label = models.CharField(
        max_length=100,
        verbose_name="متن پایین بخش",
        blank=True,
        default="PIXORIA · EST. 2010",
        help_text="متن لاتینِ کوچکِ پایین بخش. خالی بگذارید تا نمایش داده نشود",
    )

    class Meta:
        verbose_name = "بخش درباره ما (خانه)"
        verbose_name_plural = "بخش درباره ما (خانه)"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and HomeAboutSection.objects.exists():
            raise ValueError("فقط یک بخش درباره ما مجاز است")
        super().save(*args, **kwargs)

    def get_chips_list(self):
        return [chip.strip() for chip in self.chips.split(",") if chip.strip()]


class HomeAboutStat(models.Model):
    """شمارنده‌های بخش درباره ما — کارت‌های شیشه‌ای روشن با آیکون"""

    section = models.ForeignKey(
        HomeAboutSection,
        on_delete=models.CASCADE,
        related_name="stats",
        verbose_name="بخش",
        null=True,
        blank=True,
    )
    icon = models.CharField(
        max_length=64,
        default="award",
        verbose_name="آیکون",
        help_text=ICON_HELP,
        validators=[validate_icon_name],
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=1, verbose_name="مقدار", help_text="مثلاً ۱۵"
    )
    prefix = models.CharField(max_length=10, verbose_name="پیشوند", blank=True, help_text="مثلاً +")
    suffix = models.CharField(max_length=10, verbose_name="پسوند", blank=True, help_text="مثلاً ٪")
    label = models.CharField(max_length=100, verbose_name="برچسب")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "شمارندهٔ درباره ما"
        verbose_name_plural = "شمارنده‌های درباره ما"
        ordering = ["order"]

    def __str__(self):
        return self.label


class TrustedSection(models.Model):
    """بخش «برندهایی که به ما اعتماد کردند» — مارکویی برندها"""

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
        help_text=TITLE_HELP,
    )
    description = models.TextField(verbose_name="توضیحات", blank=True)
    footer_label = models.CharField(
        max_length=100,
        verbose_name="متن پایین بخش",
        blank=True,
        default="TRUSTED PARTNERS · SINCE 2010",
        help_text="متن لاتینِ کوچکِ پایین بخش. خالی بگذارید تا نمایش داده نشود",
    )

    class Meta:
        verbose_name = "بخش برندهای همکار"
        verbose_name_plural = "بخش برندهای همکار"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and TrustedSection.objects.exists():
            raise ValueError("فقط یک بخش برندهای همکار مجاز است")
        super().save(*args, **kwargs)


class TestimonialSection(models.Model):
    """بخش «نظرات مشتریان» — اسلایدر کارت‌های متنی/ویدیویی/صوتی"""

    eyebrow = models.CharField(
        max_length=100,
        verbose_name="متن بالای عنوان",
        blank=True,
        default="نظرات مشتریان",
        help_text=EYEBROW_HELP,
    )
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        help_text=TITLE_HELP + " مثال: آنچه مشتریان [[می‌گویند]]",
    )
    description = models.TextField(verbose_name="توضیحات", blank=True)

    class Meta:
        verbose_name = "بخش نظرات مشتریان"
        verbose_name_plural = "بخش نظرات مشتریان"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and TestimonialSection.objects.exists():
            raise ValueError("فقط یک بخش نظرات مجاز است")
        super().save(*args, **kwargs)


class FeaturedWorkSection(models.Model):
    """سکشن نمونه کار های منتخب"""

    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )
    title = models.CharField(
        max_length=200, verbose_name="عنوان", help_text=TITLE_HELP + " مثال: گزیدهٔ [[پروژه‌ها]]"
    )
    description = models.TextField(verbose_name="توضیحات", blank=True)

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

    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        help_text=TITLE_HELP + " مثال: از ایده تا اجرا، [[زیر یک سقف]]",
    )
    description = models.TextField(verbose_name="توضیحات", blank=True)

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
    """آیتم های مارکویی برند های همکار — هر برند یک نشان کوتاه و یک نام کامل"""

    name = models.CharField(max_length=200, verbose_name="نام برند")
    mark = models.CharField(
        max_length=20,
        verbose_name="نشان کوتاه",
        blank=True,
        help_text="کوتاه‌نام برند داخل نشان. مثلاً: رفاه. خالی بگذارید تا از نام برند استفاده شود",
    )
    accent = models.CharField(
        max_length=10,
        choices=[("gold", "طلایی"), ("royal", "آبی")],
        default="gold",
        verbose_name="رنگ نشان",
    )
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

    eyebrow = models.CharField(
        max_length=100,
        verbose_name="متن بالای عنوان",
        blank=True,
        help_text="متن کوچک و طلایی بالای عنوان. مثلاً: برند شما، امضای ما",
    )
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        help_text="کلمه‌ای که باید رنگی شود را داخل [[ ]] بنویسید.",
    )
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

    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )
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
        ("about", "درباره ما"),
        ("services", "خدمات"),
        ("trusted", "برندهای همکار"),
        ("portfolio", "نمونه‌کارها"),
        ("why", "چرا پیکسوریا"),
        ("process", "فرآیند کار"),
        ("testimonials", "نظرات مشتریان"),
        ("tech", "تکنولوژی‌ها و مهارت‌ها"),
        ("stats", "آمار و ارقام"),
        ("blog", "آخرین مقالات"),
        ("faq", "سوالات متداول"),
        ("contact", "فرم تماس سریع"),
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

    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )
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
    icon = models.CharField(
        max_length=64,
        default="award",
        verbose_name="آیکون",
        help_text=ICON_HELP,
        validators=[validate_icon_name],
    )
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

    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )
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
    icon = models.CharField(
        max_length=64,
        default="message-circle",
        verbose_name="آیکون",
        help_text=ICON_HELP,
        validators=[validate_icon_name],
    )
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

    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )
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

    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )
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
    icon = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="آیکون",
        help_text="اختیاری. مثال: figma. " + ICON_HELP,
        validators=[validate_icon_name],
    )
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

    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )
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

    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )
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
