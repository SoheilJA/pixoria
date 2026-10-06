from django.db import models

from apps.core.icon_utils import validate_icon_name

# راهنمای مشترک فیلد آیکون — آیکون‌ها از اسپرایت محلی لوساید بارگذاری می‌شوند.
ICON_HELP = (
    "نام انگلیسی یک آیکون Lucide، بدون فاصله. "
    "مثال: zap، palette، shield-check. "
    "لیست کامل آیکون‌ها: lucide.dev/icons"
)
# راهنمای مشترک فیلد متن بالای عنوان (eyebrow).
EYEBROW_HELP = "متن کوچک و طلاییِ بالای عنوان. مثلاً: نمونه‌کارها"
# راهنمای مشترک فیلد عنوان سکشن‌ها — مارکر [[ ]] کلمهٔ رنگی را مشخص می‌کند.
TITLE_HELP = "کلمه‌ای که باید رنگی شود را داخل [[ ]] بنویسید."


class PortfolioPageSection(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        help_text=TITLE_HELP + " مثال: پروژه‌هایی که [[افتخارشان]] را داریم",
    )
    description = models.TextField(verbose_name="توضیحات")
    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )

    class Meta:
        verbose_name = "هیروسکشن آرشیو نمونه کار ها"
        verbose_name_plural = "هیروسکشن آرشیو نمونه کار ها"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and PortfolioPageSection.objects.exists():
            raise ValueError("فقط یک سکشن مجاز است")
        super().save(*args, **kwargs)


class Category(models.Model):
    """دسته بندی نمونه کار ها"""

    name = models.CharField(max_length=100, verbose_name="نام")
    slug = models.SlugField(max_length=100, verbose_name="اسلاگ")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندی ها"
        ordering = ["order"]

    def __str__(self):
        return self.name

    @property
    def filter_url(self):
        """آدرس فیلترشده‌ی آرشیو نمونه‌کارها برای این دسته."""
        from django.urls import reverse

        return f"{reverse('portfolio:list')}?category={self.slug}"


class Portfolio(models.Model):
    """نمونه کار"""

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        help_text=TITLE_HELP + " مثال: فروشگاه آنلاین [[دیجی‌کالا]]",
    )
    slug = models.SlugField(max_length=200, unique=True, verbose_name="اسلاگ")
    excerpt = models.TextField(verbose_name="توضیحات کوتاه")
    description = models.TextField(verbose_name="توضیحات کامل")
    image = models.ImageField(upload_to="portfolio", verbose_name="تصویر اصلی")
    image_alt = models.CharField(
        max_length=250,
        verbose_name="متن جایگزین تصویر اصلی",
        blank=True,
        help_text="برای دسترس‌پذیری و سئو. مثال: صفحه اصلی فروشگاه دیجی‌کالا",
    )
    categories = models.ManyToManyField(Category, verbose_name="دسته بندی ها")
    client_name = models.CharField(max_length=200, verbose_name="نام مشتری")
    year = models.CharField(max_length=10, verbose_name="سال")
    service_type = models.CharField(max_length=200, verbose_name="حوزه کاری")
    client_url = models.URLField(verbose_name="لینک سایت مشتری", blank=True)
    challenge = models.TextField(verbose_name="چالش ها", blank=True)
    solution = models.TextField(verbose_name="راهکار ها", blank=True)
    technologies = models.CharField(
        max_length=500,
        verbose_name="تکنولوژی‌ها",
        blank=True,
        help_text="با کاما از هم جدا کنید. مثال: Django, React, Tailwind",
    )
    testimonial = models.ForeignKey(
        "services.ServiceTestimonial",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="portfolio_projects",
        verbose_name="نظر مشتری مرتبط",
        help_text="اختیاری. کارتِ نظر مشتری در صفحهٔ پروژه نمایش داده می‌شود",
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="توضیحات متا (سئو)",
        help_text="اختیاری. اگر خالی باشد، توضیحات کوتاه پروژه استفاده می‌شود",
    )
    featured = models.BooleanField(default=False, verbose_name="نمایش در صفحه اصلی ؟")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    created_ad = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "نمونه کار"
        verbose_name_plural = "نمونه کار ها"
        ordering = ["order"]

    def __str__(self):
        return self.title

    def get_technologies_list(self):
        """فهرست تکنولوژی‌ها از فیلد csv. مثل Service.get_chips_list."""
        return [t.strip() for t in self.technologies.split(",") if t.strip()]

    def get_meta_description(self):
        """توضیحات متا یا fallback به توضیحات کوتاه. مثل Article."""
        return self.meta_description or self.excerpt


class ProjectStat(models.Model):
    """آمار و نتایح نمونه کار"""

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="stats",
        verbose_name="نمونه کار",
    )
    number = models.CharField(max_length=50, verbose_name="عدد", help_text="مثلا +35%")
    label = models.CharField(max_length=100, verbose_name=" برچسب", blank=True)
    description = models.CharField(
        max_length=200, verbose_name="توضیحات کوتاه", blank=True
    )
    icon = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="آیکون",
        help_text="اختیاری. مثال: trending-up. " + ICON_HELP,
        validators=[validate_icon_name],
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "آمار"
        verbose_name_plural = "آمار ها"
        ordering = ["order"]

    def __str__(self):
        return f"{self.label} - {self.number}"


class ProjectImage(models.Model):
    """تصاویر گالریِ یک نمونه کار — فقط وقتی پر شوند نمایش داده می‌شوند."""

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="gallery",
        verbose_name="نمونه کار",
    )
    image = models.ImageField(
        upload_to="portfolio/gallery/", verbose_name="تصویر"
    )
    alt = models.CharField(
        max_length=250,
        verbose_name="متن جایگزین",
        blank=True,
        help_text="برای دسترس‌پذیری. اگر خالی باشد، عنوان پروژه استفاده می‌شود",
    )
    caption = models.CharField(max_length=200, verbose_name="کپشن", blank=True)
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "تصویر گالری"
        verbose_name_plural = "تصویر‌های گالری"
        ordering = ["order"]

    def __str__(self):
        return f"تصویر گالری — {self.portfolio.title}"
