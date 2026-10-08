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
    """نظرات مشتریان — سه نوع کارت در اسلایدر: متنی، ویدیویی و صوتی.

    ویدیو و صوت واقعی هستند: فایل آپلودشده یا یک آدرس مستقیم، و پخش واقعی
    مرورگر روی کارت. مدت زمان اختیاری است و وقتی خالی گذاشته شود از روی
    فرادادهٔ فایل خوانده می‌شود."""

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
    video_file = models.FileField(
        upload_to="testimonials/video/",
        verbose_name="فایل ویدیو",
        blank=True,
        help_text="فایل ویدیو (mp4/webm). آپلود فایل یا آدرس کافی است",
    )
    video_url = models.URLField(
        verbose_name="آدرس ویدیو",
        blank=True,
        help_text="آدرس مستقیم فایل ویدیو (مثلاً https://…/clip.mp4)",
    )
    video_poster = models.ImageField(
        upload_to="testimonials/video/",
        verbose_name="پوستر ویدیو",
        blank=True,
        help_text="برای کارت‌های ویدیویی. تصویر پوسترِ پیش از پخش",
    )
    video_duration = models.PositiveIntegerField(
        verbose_name="مدت زمان ویدیو (ثانیه)",
        blank=True,
        null=True,
        help_text="اختیاری — خالی بگذارید تا از روی فرادادهٔ فایل خوانده شود",
    )
    audio_file = models.FileField(
        upload_to="testimonials/audio/",
        verbose_name="فایل صوت",
        blank=True,
        help_text="فایل صوتی (mp3/m4a). آپلود فایل یا آدرس کافی است",
    )
    audio_url = models.URLField(
        verbose_name="آدرس صوت",
        blank=True,
        help_text="آدرس مستقیم فایل صوتی (مثلاً https://…/voice.mp3)",
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
        verbose_name="مدت زمان صوت (ثانیه)",
        blank=True,
        null=True,
        help_text="اختیاری — خالی بگذارید تا از روی فرادادهٔ فایل خوانده شود",
    )
    show_on_home = models.BooleanField(default=False, verbose_name="نمایش در صفحه اصلی")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "نظر مشتری"
        verbose_name_plural = "نظرات مشتریان"
        ordering = ["order"]

    def __str__(self):
        return f"{self.author_name} — {self.service.title}"

    def get_video_src(self):
        """آدرس پخش ویدیو: فایل آپلودشده، وگرنه آدرس مستقیم."""
        if self.video_file:
            return self.video_file.url
        return self.video_url or ""

    def get_audio_src(self):
        """آدرس پخش صوت: فایل آپلودشده، وگرنه آدرس مستقیم."""
        if self.audio_file:
            return self.audio_file.url
        return self.audio_url or ""

    def clean(self):
        from django.core.exceptions import ValidationError

        super().clean()
        if self.kind == "text":
            if not self.text:
                raise ValidationError({"text": "کارت متنی به متنِ نظر نیاز دارد."})
        elif self.kind == "video":
            errors = {}
            if not (self.video_file or self.video_url):
                errors["video_file"] = "ویدیو به فایل یا آدرسِ ویدیو نیاز دارد."
                errors["video_url"] = "ویدیو به فایل یا آدرسِ ویدیو نیاز دارد."
            if not self.video_poster:
                errors["video_poster"] = "ویدیو به پوستر نیاز دارد."
            if errors:
                raise ValidationError(errors)
        elif self.kind == "audio":
            errors = {}
            if not (self.audio_file or self.audio_url):
                errors["audio_file"] = "صوت به فایل یا آدرسِ صوت نیاز دارد."
                errors["audio_url"] = "صوت به فایل یا آدرسِ صوت نیاز دارد."
            if not self.audio_title:
                errors["audio_title"] = "کارت صوتی به عنوان نیاز دارد."
            if errors:
                raise ValidationError(errors)
