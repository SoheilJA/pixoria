from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.icon_utils import validate_icon_name


class ServicesPageSection(models.Model):
    """هیرو صفحه همه خدمات"""

    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    class Meta:
        verbose_name = "سکشن صفحه خدمات"
        verbose_name_plural = "سکشن صفحه خدمات"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and ServicesPageSection.objects.exists():
            raise ValueError("فقط یک سکشن مجاز است")
        super().save(*args, **kwargs)


class Service(models.Model):
    """خدمت — در صفحه اصلی به‌صورت کارت‌های اختصاصی v2 با تصویرسازی اختصاصی رندر
    می‌شود."""

    VISUAL_CHOICES = [
        ("none", "بدون تصویرسازی"),
        ("browser", "ماکت مرورگر"),
        ("terminal", "ترمینال"),
        ("palette", "پالت رنگی و پوستر"),
        ("diamond", "شبکهٔ راهنمای لوگو"),
    ]
    SPAN_CHOICES = [
        ("wide", "عریض (۷ ستون)"),
        ("narrow", "کوچک (۵ ستون)"),
    ]

    title = models.CharField(max_length=200, verbose_name="عنوان")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="اسلاگ")
    excerpt = models.TextField(verbose_name="توضیحات کوتاه")
    description = models.TextField(verbose_name="توضیحات کامل صفحه خدمت")
    icon = models.CharField(
        max_length=64,
        default="sparkles",
        verbose_name="آیکون",
        help_text=(
            "نام انگلیسی یک آیکون Lucide، بدون فاصله. "
            "مثال: monitor-smartphone، code-xml، palette، diamond. "
            "لیست کامل آیکون‌ها: lucide.dev/icons"
        ),
        validators=[validate_icon_name],
    )
    visual = models.CharField(
        max_length=10,
        choices=VISUAL_CHOICES,
        default="none",
        verbose_name="تصویرسازی کارت",
        help_text="تصویرسازی اختصاصیِ کارت در صفحه اصلی (ماکت مرورگر، ترمینال و ...)",
    )
    card_span = models.CharField(
        max_length=10,
        choices=SPAN_CHOICES,
        default="narrow",
        verbose_name="عرض کارت در صفحه اصلی",
    )
    chips = models.CharField(
        max_length=500,
        verbose_name="برچسب‌های کارت",
        blank=True,
        help_text="با ویرگول جدا کنید. مثلاً: واکنش‌گرا، سئو-friendly، پشتیبانی مستمر",
    )
    badge = models.CharField(
        max_length=100,
        verbose_name="نشان شناورِ کارت",
        blank=True,
        help_text="متن نشان شیشه‌ای شناور روی تصویرسازی. مثلاً: ۹۹/۱۰۰ · Core Web Vitals",
    )
    tags = models.CharField(
        max_length=500,
        verbose_name="تگ‌ها",
        help_text="با ویرگول جدا کنید. مثلاً: سئو, محتوا, لینک سازی",
    )
    featured = models.BooleanField(default=True, verbose_name="نمایش در صفحه اصلی")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "خدمت"
        verbose_name_plural = "خدمات"
        ordering = ["order"]

    def __str__(self):
        return self.title

    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    def get_chips_list(self):
        return [chip.strip() for chip in self.chips.split(",") if chip.strip()]


class ServiceStat(models.Model):
    """آمار خدمت"""

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="stats", verbose_name="خدمت"
    )
    number = models.CharField(
        max_length=50, verbose_name="عدد", help_text="مثلاً +۸۰ یا ۹۷٪"
    )
    label = models.CharField(max_length=100, verbose_name="برچسب")
    description = models.CharField(
        max_length=200, verbose_name="توضیح کوتاه", blank=True
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "آمار"
        verbose_name_plural = "آمارها"
        ordering = ["order"]

    def __str__(self):
        return f"{self.label} — {self.number}"


class ServiceWhyUs(models.Model):
    """چرا ما — مزایای خدمت"""

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="why_us", verbose_name="خدمت"
    )
    icon = models.CharField(
        max_length=64,
        default="sparkles",
        verbose_name="آیکون",
        help_text=(
            "نام انگلیسی یک آیکون Lucide، بدون فاصله. "
            "مثال: zap، palette، shield-check. "
            "لیست کامل آیکون‌ها: lucide.dev/icons"
        ),
        validators=[validate_icon_name],
    )
    title = models.CharField(max_length=100, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "مزیت"
        verbose_name_plural = "مزایا"
        ordering = ["order"]

    def __str__(self):
        return self.title


class ServiceDeliverable(models.Model):
    """خروجی‌های خدمت"""

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="deliverables",
        verbose_name="خدمت",
    )
    title = models.CharField(max_length=200, verbose_name="عنوان")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "خروجی"
        verbose_name_plural = "خروجی‌ها"
        ordering = ["order"]

    def __str__(self):
        return self.title


class ServiceProcess(models.Model):
    """فرآیند کار"""

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="processes", verbose_name="خدمت"
    )
    title = models.CharField(max_length=200, verbose_name="عنوان مرحله")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "مرحله"
        verbose_name_plural = "مراحل"
        ordering = ["order"]

    def __str__(self):
        return self.title


class ServicePlan(models.Model):
    """پلن قیمت‌گذاری"""

    PLAN_TYPE_CHOICES = [
        ("starter", "استارتر"),
        ("pro", "پیشرفته"),
        ("enterprise", "اختصاصی"),
    ]
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="plans", verbose_name="خدمت"
    )
    plan_type = models.CharField(
        max_length=20, choices=PLAN_TYPE_CHOICES, verbose_name="نوع پلن"
    )
    name = models.CharField(max_length=100, verbose_name="نام پلن")
    price = models.CharField(
        max_length=50, verbose_name="قیمت", help_text="مثلاً ۱۲ یا از ۵۰"
    )
    old_price = models.CharField(
        max_length=50, verbose_name="قیمت قبل از تخفیف", blank=True
    )
    discount_label = models.CharField(
        max_length=50,
        verbose_name="برچسب تخفیف",
        blank=True,
        help_text="مثلاً ۲۰٪ تخفیف",
    )
    is_featured = models.BooleanField(default=False, verbose_name="پلن پیشنهادی؟")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "پلن"
        verbose_name_plural = "پلن‌ها"
        ordering = ["order"]

    def __str__(self):
        return f"{self.service.title} — {self.name}"


class ServicePlanFeature(models.Model):
    """ویژگی‌های پلن"""

    plan = models.ForeignKey(
        ServicePlan,
        on_delete=models.CASCADE,
        related_name="features",
        verbose_name="پلن",
    )
    title = models.CharField(max_length=200, verbose_name="عنوان ویژگی")
    included = models.BooleanField(default=True, verbose_name="شامل میشه؟")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "ویژگی"
        verbose_name_plural = "ویژگی‌ها"
        ordering = ["order"]

    def __str__(self):
        return self.title


class ServiceCustomItem(models.Model):
    """آیتم‌های پلن سفارشی"""

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="custom_items",
        verbose_name="خدمت",
    )
    title = models.CharField(max_length=200, verbose_name="عنوان آیتم")
    description = models.CharField(
        max_length=200, verbose_name="توضیح کوتاه", blank=True
    )
    price = models.PositiveIntegerField(verbose_name="قیمت (میلیون تومان)")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "آیتم سفارشی"
        verbose_name_plural = "آیتم‌های سفارشی"
        ordering = ["order"]

    def __str__(self):
        return self.title


class ServiceFAQ(models.Model):
    """سوالات متداول"""

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="faqs", verbose_name="خدمت"
    )
    question = models.CharField(max_length=300, verbose_name="سوال")
    answer = models.TextField(verbose_name="جواب")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "سوال متداول"
        verbose_name_plural = "سوالات متداول"
        ordering = ["order"]

    def __str__(self):
        return self.question


class ServiceTestimonial(models.Model):
    """نظرات مشتریان — سه نوع کارت در اسلایدر صفحه اصلی: متنی، ویدیویی و صوتی.
    پخش ویدیو و صدا در مرورگر شبیه‌سازی می‌شود؛ بنابراین فقط پوستر و مدت
    زمان نمایش داده می‌شود."""

    KIND_CHOICES = [
        ("text", "متن"),
        ("video", "ویدیو"),
        ("audio", "صوت"),
    ]

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="testimonials",
        verbose_name="خدمت",
    )
    kind = models.CharField(
        max_length=10,
        choices=KIND_CHOICES,
        default="text",
        verbose_name="نوع کارت",
    )
    author_name = models.CharField(max_length=100, verbose_name="نام")
    author_role = models.CharField(max_length=200, verbose_name="نقش و شرکت")
    author_image = models.ImageField(
        upload_to="testimonials/", verbose_name="تصویر", blank=True
    )
    text = models.TextField(verbose_name="متن نظر", blank=True)
    rating = models.PositiveIntegerField(
        default=5,
        verbose_name="امتیاز (۱ تا ۵)",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    video_poster = models.ImageField(
        upload_to="testimonials/video/",
        verbose_name="پوستر ویدیو",
        blank=True,
        help_text="برای کارت‌های ویدیویی. تصویر پوسترِ پیش از پخش",
    )
    video_duration = models.PositiveIntegerField(
        default=48,
        verbose_name="مدت زمان ویدیو (ثانیه)",
        help_text="در مرورگر شبیه‌سازی می‌شود؛ فقط برای نمایش زمان",
    )
    audio_title = models.CharField(
        max_length=200,
        verbose_name="عنوان پیام صوتی",
        blank=True,
        help_text="مثلاً: گفت‌وگو با کارفرما",
    )
    audio_project = models.CharField(
        max_length=200,
        verbose_name="پروژهٔ پیام صوتی",
        blank=True,
        help_text="مثلاً: پروژهٔ همایش ملی",
    )
    audio_duration = models.PositiveIntegerField(
        default=65,
        verbose_name="مدت زمان صوت (ثانیه)",
        help_text="در مرورگر شبیه‌سازی می‌شود؛ فقط برای نمایش زمان",
    )
    show_on_home = models.BooleanField(default=False, verbose_name="نمایش در صفحه اصلی")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "نظر مشتری"
        verbose_name_plural = "نظرات مشتریان"
        ordering = ["order"]

    def __str__(self):
        return f"{self.author_name} — {self.service.title}"
