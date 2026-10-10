from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from tinymce.models import HTMLField

from apps.core.icon_utils import validate_icon_name
from apps.core.models import EYEBROW_HELP, ICON_HELP, TITLE_HELP, URL_HELP


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
    # لهجهٔ رنگیِ صفحهٔ اختصاصیِ خدمت — به کلاسِ svc-accent-* در input.css
    # نگاشت می‌شود (T60) و حلقه‌ها/سیاره/خطوطِ صفحه را رنگ می‌کند.
    ACCENT_CHOICES = [
        ("gold", "طلایی"),
        ("gold-light", "طلاییِ روشن"),
        ("gold-dark", "طلاییِ تیره"),
        ("royal", "آبیِ سلطنتی"),
        ("cream", "کرم"),
        ("peri", "آبیِ کم‌رنگ"),
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

    # --- لهجهٔ رنگیِ صفحهٔ اختصاصی ---
    accent = models.CharField(
        max_length=20,
        choices=ACCENT_CHOICES,
        default="gold",
        verbose_name="رنگِ تم (لهجه)",
        help_text="رنگِ حلقه‌ها، سیاره و خطوطِ صفحهٔ اختصاصیِ این خدمت",
    )

    # --- هیروی صفحهٔ اختصاصی ---
    hero_eyebrow = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="متن بالای عنوان",
        help_text=EYEBROW_HELP + ". مثال: خدمات طراحی سایت در مشهد",
    )
    hero_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="عنوان هیرو",
        help_text=TITLE_HELP + " مثال: طراحی سایتی که [[می‌فروشد]]",
    )
    hero_lead = models.TextField(
        blank=True, verbose_name="مقدمهٔ هیرو", help_text="پاراگرافِ زیرِ عنوان"
    )
    hero_cta_primary_text = models.CharField(
        max_length=50, blank=True, verbose_name="متن دکمهٔ اصلی"
    )
    hero_cta_primary_url = models.CharField(
        max_length=200, blank=True, verbose_name="لینک دکمهٔ اصلی", help_text=URL_HELP
    )
    hero_cta_secondary_text = models.CharField(
        max_length=50, blank=True, verbose_name="متن دکمهٔ دوم"
    )
    hero_cta_secondary_url = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="لینک دکمهٔ دوم",
        help_text=URL_HELP + ". خالی بگذارید تا دکمه نمایش داده نشود",
    )

    # --- سئو ---
    meta_title = models.CharField(
        max_length=70, blank=True, verbose_name="عنوان متا (سئو)"
    )
    meta_description = models.CharField(
        max_length=160, blank=True, verbose_name="توضیحات متا (سئو)"
    )
    og_image = models.ImageField(
        upload_to="services/og/",
        blank=True,
        verbose_name="تصویر شبکه‌های اجتماعی",
        help_text="اختیاری. تصویرِ og:this صفحه؛ خالی → از لوگوی سایت استفاده می‌شود",
    )

    # --- خدمات مرتبط ---
    related_services = models.ManyToManyField(
        "self",
        blank=True,
        verbose_name="خدمات مرتبط",
        help_text="اختیاری. کارتِ خدماتِ مرتبط پایینِ صفحهٔ اختصاصی نشان داده می‌شود",
    )

    class Meta:
        verbose_name = "خدمت"
        verbose_name_plural = "خدمات"
        ordering = ["order"]

    def __str__(self):
        return self.title

    @property
    def accent_class(self):
        """کلاس CSSِ تمِ این خدمت — svc-accent-* در input.css."""
        return f"svc-accent-{self.accent}"

    def get_meta_title(self):
        """عنوان متا یا fallback به عنوانِ خدمت."""
        return self.meta_title or self.title

    def get_meta_description(self):
        """توضیحات متا یا fallback به توضیحات کوتاه."""
        return self.meta_description or self.excerpt

    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    def get_chips_list(self):
        return [chip.strip() for chip in self.chips.split(",") if chip.strip()]


class ServiceSection(models.Model):
    """بخشِ محتوای بلندِ صفحهٔ اختصاصیِ خدمت — سئو-friendly، هر تعداد که ادمین
    بخواهد. چیدمانِ تصویر را ``layout`` تعیین می‌کند و ``is_active`` یک بخش را
    بدون حذف کردن مخفی می‌کند."""

    LAYOUT_CHOICES = [
        ("right", "تصویر سمت راست"),
        ("left", "تصویر سمت چپ"),
        ("full", "تمام‌عرض (بدون تصویر کناری)"),
    ]

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name="خدمت",
    )
    eyebrow = models.CharField(
        max_length=100, blank=True, verbose_name="متن بالای عنوان", help_text=EYEBROW_HELP
    )
    title = models.CharField(
        max_length=200, verbose_name="عنوان", help_text=TITLE_HELP
    )
    body = HTMLField(verbose_name="متن")
    image = models.ImageField(
        upload_to="services/sections/", blank=True, verbose_name="تصویر"
    )
    image_alt = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="متن جایگزین تصویر",
        help_text="برای دسترس‌پذیری و سئو. مثال: پروسهٔ طراحیِ سایت پیکسوریا",
    )
    layout = models.CharField(
        max_length=10,
        choices=LAYOUT_CHOICES,
        default="right",
        verbose_name="چیدمان",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "بخش محتوا"
        verbose_name_plural = "بخش‌های محتوا"
        ordering = ["order"]

    def __str__(self):
        return f"{self.service.title} — {self.title}"


class ServiceTool(models.Model):
    """ابزارها و فناوری‌های یک خدمت — چیپ‌های صفحهٔ اختصاصی."""

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="tools",
        verbose_name="خدمت",
    )
    name = models.CharField(max_length=100, verbose_name="نام")
    icon = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="آیکون",
        help_text="اختیاری. " + ICON_HELP,
        validators=[validate_icon_name],
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "ابزار"
        verbose_name_plural = "ابزارها"
        ordering = ["order"]

    def __str__(self):
        return self.name


class ServiceUseCase(models.Model):
    """صنایع و کاربردهای یک خدمت."""

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="use_cases",
        verbose_name="خدمت",
    )
    title = models.CharField(max_length=100, verbose_name="عنوان")
    icon = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="آیکون",
        help_text="اختیاری. " + ICON_HELP,
        validators=[validate_icon_name],
    )
    description = models.CharField(
        max_length=200, verbose_name="متن کوتاه", blank=True
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "کاربرد / صنعت"
        verbose_name_plural = "کاربردها / صنایع"
        ordering = ["order"]

    def __str__(self):
        return f"{self.service.title} — {self.title}"


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
    description = models.TextField(
        max_length=400,
        blank=True,
        verbose_name="توضیح کوتاه مرحله",
        help_text="یک جمله دربارهٔ این مرحله (الزامى نیست).",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "مرحله"
        verbose_name_plural = "مراحل"
        ordering = ["order"]

    def __str__(self):
        return self.title


class ServicePlan(models.Model):
    """پلن قیمت‌گذاری — دقیقاً سه پلن برای هر خدمت (max_num=3 در ادمین).
    قیمت یک عددِ اختیاری است (تومان)؛ وقتی خالی باشد ``price_note`` نمایش
    داده می‌شود (مثل «تماس بگیرید»)."""

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
    tagline = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="خلاصهٔ کوتاه",
        help_text="یک جملهٔ زیرِ نام پلن. مثلاً: برای کسب‌وکارهای تازه شروع‌شده",
    )
    price = models.PositiveBigIntegerField(
        blank=True,
        null=True,
        verbose_name="قیمت (تومان)",
        help_text="عددِ اختیاری. مثلاً 15000000. خالی → قیمت نهایی «تماس بگیرید» است",
    )
    price_prefix = models.CharField(
        max_length=20,
        blank=True,
        default="از",
        verbose_name="پیشوندِ قیمت",
        help_text="مثلاً «از». قبل از قیمت می‌آید: از ۱۵٬۰۰۰٬۰۰۰ تومان",
    )
    price_currency = models.CharField(
        max_length=20, default="تومان", verbose_name="واحدِ پول"
    )
    price_note = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="متنِ جایگزینِ قیمت",
        help_text="وقتی قیمت خالی است نمایش داده می‌شود. مثلاً: تماس بگیرید",
    )
    old_price = models.PositiveBigIntegerField(
        blank=True,
        null=True,
        verbose_name="قیمت قبل از تخفیف",
        help_text="عددِ اختیاری. خط‌خورده بالای قیمت نشان داده می‌شود",
    )
    discount_label = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="برچسب تخفیف",
        help_text="مثلاً ۲۰٪ تخفیف",
    )
    cta_label = models.CharField(
        max_length=50, blank=True, verbose_name="متن دکمهٔ پلن"
    )
    cta_url = models.CharField(
        max_length=200, blank=True, verbose_name="لینک دکمهٔ پلن", help_text=URL_HELP
    )
    is_featured = models.BooleanField(default=False, verbose_name="پلن پیشنهادی؟")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    # کدِ ISO 4217 برای داده‌های ساختاریافته — schema.org فقط کدِ سه‌حرفیِ
    # واحدِ پول را می‌پذیرد (IRT = تومانِ ایران، IRR = ریالِ ایران).
    CURRENCY_CODES = {"تومان": "IRT", "ریال": "IRR"}

    class Meta:
        verbose_name = "پلن"
        verbose_name_plural = "پلن‌ها"
        ordering = ["order"]

    @property
    def price_currency_code(self):
        """کدِ ISO 4217ِ واحدِ پول برای JSON-LD (پیش‌فرض: IRT)."""
        return self.CURRENCY_CODES.get((self.price_currency or "").strip(), "IRT")

    def __str__(self):
        return f"{self.service.title} — {self.name}"

    def clean(self):
        super().clean()
        # فقط یک پلنِ پیشنهادی برای هر خدمت — در غیر این صورت نشانِ
        # «محبوب‌ترین» بی‌معنی می‌شود.
        if self.is_featured and self.service_id:
            others = ServicePlan.objects.filter(
                service_id=self.service_id, is_featured=True
            )
            if self.pk:
                others = others.exclude(pk=self.pk)
            if others.exists():
                raise ValidationError(
                    {
                        "is_featured": (
                            "برای هر خدمت فقط یک پلن می‌تواند «پیشنهادی» باشد."
                        )
                    }
                )


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
