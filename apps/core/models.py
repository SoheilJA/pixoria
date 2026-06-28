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
