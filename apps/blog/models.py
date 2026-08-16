from math import ceil

from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
from tinymce.models import HTMLField


class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="اسلاگ")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True, verbose_name="عنوان برچسب")

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"

    def __str__(self):
        return self.title


class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام")
    role = models.CharField(
        max_length=150,
        verbose_name="عنوان شغلی",
        help_text="مثلاً: استراتژیست سئو · بنیان‌گذار",
    )
    avatar = models.ImageField(
        upload_to="blog/authors/", blank=True, verbose_name="تصویر نویسنده"
    )
    bio = models.TextField(max_length=300, verbose_name="بیوگرافی کوتاه")

    class Meta:
        verbose_name = "نویسنده"
        verbose_name_plural = "نویسندگان"

    def __str__(self):
        return self.name

    def initial(self):
        return self.name[:1] if self.name else "؟"


class Article(models.Model):
    STATUS_CHOICES = [
        ("draft", "پیش‌نویس"),
        ("published", "منتشر شده"),
    ]

    title = models.CharField(max_length=250, verbose_name="عنوان")
    slug = models.SlugField(max_length=250, unique=True, verbose_name="اسلاگ")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name="دسته‌بندی",
    )
    tags = models.ManyToManyField(
        Tag, blank=True, related_name="articles", verbose_name="برچسب‌ها"
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        related_name="articles",
        verbose_name="نویسنده",
    )

    cover_image = models.ImageField(upload_to="blog/covers/", verbose_name="تصویر کاور")
    cover_image_alt = models.CharField(
        max_length=250, verbose_name="متن جایگزین تصویر کاور"
    )

    excerpt = models.TextField(max_length=300, verbose_name="خلاصه مقاله")
    content = HTMLField(verbose_name="محتوای مقاله")

    reading_time = models.PositiveIntegerField(
        default=1, editable=False, verbose_name="زمان مطالعه (دقیقه)"
    )

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="draft", verbose_name="وضعیت"
    )
    published_at = models.DateTimeField(
        default=timezone.now, verbose_name="تاریخ انتشار"
    )

    meta_title = models.CharField(
        max_length=70, blank=True, verbose_name="عنوان متا (سئو)"
    )
    meta_description = models.CharField(
        max_length=160, blank=True, verbose_name="توضیحات متا (سئو)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        word_count = len(strip_tags(self.content).split())
        self.reading_time = max(1, ceil(word_count / 200))
        super().save(*args, **kwargs)

    def get_meta_title(self):
        return self.meta_title or self.title

    def get_meta_description(self):
        return self.meta_description or self.excerpt

    def is_updated(self):
        return (self.updated_at - self.published_at).days >= 1


class BlogPageSettings(models.Model):
    title = models.CharField(
        max_length=100, verbose_name="عنوان صفحه بلاگ", help_text="مثلاً: دانش،"
    )
    title_highlight = models.CharField(
        max_length=100,
        verbose_name="بخش هایلایت‌شده عنوان",
        help_text="مثلاً: بی‌واسطه.",
    )
    description = models.TextField(verbose_name="توضیحات صفحه بلاگ")

    class Meta:
        verbose_name = "تنظیمات صفحه بلاگ"
        verbose_name_plural = "تنظیمات صفحه بلاگ"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and BlogPageSettings.objects.exists():
            raise ValueError("فقط یک تنظیمات صفحه بلاگ مجاز است")
        super().save(*args, **kwargs)
