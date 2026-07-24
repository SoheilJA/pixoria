from django.db import models


class ContactPageSection(models.Model):
    """عنوان و توضیحات صفحه تماس با ما"""

    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    class Meta:
        verbose_name = "هیروسکشن صفحه تماس"
        verbose_name_plural = "هیروسکشن صفحه تماس"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and ContactPageSection.objects.exists():
            raise ValueError("فقط یک سکشن مجاز است")
        super().save(*args, **kwargs)


class ContactInfo(models.Model):
    """اطلاعات تماس سمت راست"""

    office_title = models.CharField(
        max_length=100, verbose_name="عنوان دفتر", help_text="مثال: مشهد"
    )
    office_address = models.TextField(verbose_name="آدرس دفتر")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    working_hours = models.CharField(max_length=100, verbose_name="ساعت کاری")
    email_project = models.EmailField(
        verbose_name="ایمیل پروژه‌های جدید", blank=True,
        help_text="مثال: project@example.com"
    )
    email_press = models.EmailField(
        verbose_name="ایمیل رسانه", blank=True
    )
    email_career = models.EmailField(
        verbose_name="ایمیل فرصت‌های شغلی", blank=True
    )
    tagline = models.CharField(
        max_length=200, verbose_name="جمله کوتاه / شعار", blank=True,
        help_text="یک جمله کوتاه در ستون تماس نمایش داده می‌شود"
    )

    class Meta:
        verbose_name = "اطلاعات تماس"
        verbose_name_plural = "اطلاعات تماس"

    def __str__(self):
        return self.office_title

    def save(self, *args, **kwrgs):
        if not self.pk and ContactInfo.objects.exists():
            raise ValueError("فقط یک اطلاعات تماس مجاز است")
        super().save(*args, **kwrgs)


class ProjectTypeChoice(models.Model):
    """گزینه های نوع پروژه"""

    label = models.CharField(max_length=100, verbose_name="گزینه")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "نوع پروژه"
        verbose_name_plural = "انواع پروژه"
        ordering = ["order"]

    def __str__(self):
        return self.label


class BudgetChoice(models.Model):
    """گزینه های بودجه"""

    label = models.CharField(max_length=100, verbose_name="گزینه")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "بودجه"
        verbose_name_plural = "بودجه ها"
        ordering = ["order"]

    def __str__(self):
        return self.label


class StartTimeChoice(models.Model):
    """گزینه های زمان شروع"""

    label = models.CharField(max_length=100, verbose_name="گزینه")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "زمان شروع"
        verbose_name_plural = "زمان های شروع"
        ordering = ["order"]

    def __str__(self):
        return self.label


class ContactSubmission(models.Model):
    """فرم های ارسال شده توسط کاربران"""

    STATUS_CHOICES = [("new", "جدید"), ("seen", "مشاهده شده")]

    name = models.CharField(max_length=200, verbose_name="نام و نام خانوادگی")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    company = models.CharField(
        max_length=200, verbose_name="نام شرکت", blank=True, null=True
    )
    project_type = models.CharField(max_length=100, verbose_name="نوع پروژه")
    budget = models.CharField(max_length=100, verbose_name="بودجه")
    start_time = models.CharField(max_length=100, verbose_name="زمان شروع پروژه")
    message = models.TextField(verbose_name="توضیحات پروژه", blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="new", verbose_name="وضعیت"
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")

    class Meta:
        verbose_name = "فرم تماس"
        verbose_name_plural = "فرم های تماس"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.name} - {self.submitted_at.strftime('%Y/%m/%d')}"
