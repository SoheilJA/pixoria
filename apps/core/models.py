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


"""مدل های صفحه درباره ما"""


class AboutPageHero(models.Model):
    """هیرو سکشن درباره ما"""

    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    class Meta:
        verbose_name = "هیروسکشن صفحه درباره ما"
        verbose_name_plural = "هیروسکشن صفحه درباره ما"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and AboutPageHero.objects.exists():
            raise ValueError("فقط یک هیرو مجاز است")
        super().save(*args, **kwargs)


class AboutStory(models.Model):
    """داستان ما"""

    description = models.TextField(verbose_name="توضیحات ")

    class Meta:
        verbose_name = "داستان ما"
        verbose_name_plural = "داستان ما"

    def __str__(self):
        return "داستان ما"

    def save(self, *args, **kwargs):
        if not self.pk and AboutStory.objects.exists():
            raise ValueError("فقط یک سکشن مجاز است")
        super().save(*args, **kwargs)


class TeamMember(models.Model):
    """اعضای تیم"""

    name = models.CharField(max_length=100, verbose_name="نام")
    role = models.TextField(verbose_name="نقش")
    bio = models.TextField(verbose_name="توضیحات")
    image = models.ImageField(upload_to="team/", verbose_name="تصویر")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "عضو تیم"
        verbose_name_plural = "اعضای تیم"
        ordering = ["order"]

    def __str__(self):
        return self.name


class AboutValue(models.Model):
    """ارزش های سئو ران"""

    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "ارزش"
        verbose_name_plural = "ارزش ها"
        ordering = ["order"]

    def __str__(self):
        return self.title


class AboutStat(models.Model):
    """آمار و ارقام"""

    number = models.CharField(max_length=50, verbose_name="عدد", help_text="مثلا +70")
    label = models.CharField(max_length=100, verbose_name="برچست")
    description = models.CharField(
        max_length=200, verbose_name="توضیحات کوتاه", blank=True
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "آمار"
        verbose_name_plural = "امار و ارقام"
        ordering = ["order"]

    def __str__(self):
        return self.label


class AboutPre(models.Model):
    """پریفوتر درباره ما"""

    label = models.CharField(max_length=100, verbose_name="ساب تایتل")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")
    button_text = models.CharField(max_length=100, verbose_name="متن دکمه")
    button_url = models.CharField(max_length=200, verbose_name="لینک دکمه")

    class Meta:
        verbose_name = "سکشن پریفوتر درباه ما"
        verbose_name_plural = "سکشن پریفوتر درباره ما"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and AboutPre.objects.exists():
            raise ValueError("فقط یک سکشن مجاز است")
        super().save(*args, **kwargs)
