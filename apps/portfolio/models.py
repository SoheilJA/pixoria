from django.db import models


class PortfolioPageSection(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

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


class Portfolio(models.Model):
    """نمونه کار"""

    title = models.CharField(max_length=200, verbose_name="عنوان")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="اسلاگ")
    excerpt = models.TextField(verbose_name="توضیحات کوتاه")
    description = models.TextField(verbose_name="توضیحات کامل")
    image = models.ImageField(upload_to="portfolio", verbose_name="تصویر اصلی")
    categories = models.ManyToManyField(Category, verbose_name="دسته بندی ها")
    client_name = models.CharField(max_length=200, verbose_name="نام مشتری")
    year = models.CharField(max_length=10, verbose_name="سال")
    service_type = models.CharField(max_length=200, verbose_name="حوزه کاری")
    client_url = models.URLField(verbose_name="لینک سایت مشتری", blank=True)
    challenge = models.TextField(verbose_name="چالش ها", blank=True)
    solution = models.TextField(verbose_name="راهکار ها", blank=True)
    featured = models.BooleanField(default=False, verbose_name="نمایش در صفحه اصلی ؟")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    created_ad = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "نمونه کار"
        verbose_name_plural = "نمونه کار ها"
        ordering = ["order"]

    def __str__(self):
        return self.title


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
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "آمار"
        verbose_name_plural = "آمار ها"
        ordering = ["order"]

    def __str__(self):
        return f"{self.label} - {self.number}"
