from math import ceil

from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
from tinymce.models import HTMLField


class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="اسلاگ")

    class Meta:
        verbose_name = " دسته بندی"
        verbose_name_plural = "دسته بندی ها"

    def __str__(self):
        return self.title


class Article(models.Model):
    STATUS_CHOICES = [("draft", "پیش نویس"), ("published", "منتشر شده")]

    title = models.CharField(max_length=250, verbose_name="عنوان")
    slug = models.SlugField(max_length=250, unique=True, verbose_name="اسلاگ")

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name="دسته بندی",
    )

    cover_image = models.ImageField(upload_to="blog/covers/", verbose_name="تصویر کاور")
    cover_image_alt = models.CharField(max_length=250, verbose_name="متن جایگزین تصویر")

    excerpt = models.TextField(max_length=300, verbose_name="خلاصه مقاله")
    content = HTMLField(verbose_name="محتوای مقاله")

    reading_time = models.PositiveIntegerField(
        default=1, editable=False, verbose_name="زمان مطالعه (دقیقه)"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="وضعیت مقاله",
    )
    published_at = models.DateTimeField(
        default=timezone.now, verbose_name="تاریخ انتشار"
    )

    meta_title = models.CharField(max_length=70, blank=True, verbose_name="عنوان متا")
    meta_descripton = models.CharField(
        max_length=160, blank=True, verbose_name="توضیحات متا"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, args, **kwargs):
        word_count = len(strip_tags(self.content).split())
        self.reading_time = max(1, ceil(word_count / 200))
        super().save(*args, **kwargs)

    def get_meta_title(self):
        return self.meta_title or self.title

    def get_meta_description(self):
        return self.meta_descripton or self.excerpt
