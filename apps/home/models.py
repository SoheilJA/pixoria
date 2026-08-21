from django.db import models


class HeroSection(models.Model):
    """هیرو سکشن"""

    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    class Meta:
        verbose_name = "هیرو سکشن"
        verbose_name_plural = "هیرو سکشن"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and HeroSection.objects.exists():
            raise ValueError("فقط یک هیروسکشن مجاز است")
        super().save(*args, **kwargs)


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


class FeaturedWorkSection(models.Model):
    """سکشن نمونه کار های منتخب"""

    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

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

    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

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
    """آیتم های مارکویی برند های همکار"""

    name = models.CharField(max_length=200, verbose_name="نام برند")
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

    title = models.CharField(max_length=200, verbose_name="عنوان")
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
