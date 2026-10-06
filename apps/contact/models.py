from django.db import models

from apps.core.icon_utils import validate_icon_name

# راهنمای مشترک فیلد آیکون — آیکون‌ها از اسپرایت محلی لوساید بارگذاری می‌شوند.
ICON_HELP = (
    "نام انگلیسی یک آیکون Lucide، بدون فاصله. "
    "مثال: zap، palette، shield-check. "
    "لیست کامل آیکون‌ها: lucide.dev/icons"
)
# راهنمای مشترک فیلد متن بالای عنوان (eyebrow).
EYEBROW_HELP = "متن کوچک و طلاییِ بالای عنوان. مثلاً: تماس با ما"
# راهنمای مشترک فیلد عنوان سکشن‌ها — مارکر [[ ]] کلمهٔ رنگی را مشخص می‌کند.
TITLE_HELP = "کلمه‌ای که باید رنگی شود را داخل [[ ]] بنویسید."


class ContactPageSection(models.Model):
    """عنوان و توضیحات صفحه تماس با ما"""

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        help_text=TITLE_HELP + " مثال: بیایید [[گفت‌وگو]] کنیم",
    )
    description = models.TextField(verbose_name="توضیحات")
    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )
    response_note = models.CharField(
        max_length=200,
        verbose_name="یادداشت پاسخ‌گویی",
        blank=True,
        help_text="خط کوچک زیر توضیحات هیرو. مثلاً: پاسخ‌گویی در روزهای کاری، حداکثر تا ۲۴ ساعت",
    )

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


class ContactFormSection(models.Model):
    """تنظیمات بخش فرم تماس (روشن) — ستون کنار فرم"""

    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        blank=True,
        help_text=TITLE_HELP + " مثال: پیامِ شما، شروعِ یک [[همکاری]]",
    )
    description = models.TextField(verbose_name="توضیحات", blank=True)
    button_text = models.CharField(
        max_length=50, verbose_name="متن دکمهٔ ارسال", default="ارسال پیام"
    )
    note = models.CharField(
        max_length=200,
        verbose_name="یادداشت زیر دکمه",
        blank=True,
        help_text="مثلاً: اطلاعات شما فقط برای پاسخ‌گویی استفاده می‌شود.",
    )

    class Meta:
        verbose_name = "بخش فرم تماس"
        verbose_name_plural = "بخش فرم تماس"

    def __str__(self):
        return "بخش فرم تماس"

    def save(self, *args, **kwargs):
        if not self.pk and ContactFormSection.objects.exists():
            raise ValueError("فقط یک سکشن مجاز است")
        super().save(*args, **kwargs)


class ContactFormPoint(models.Model):
    """مزایای کنار فرم تماس — مشاورهٔ رایگان، موقعیت، ساعت کاری و …"""

    section = models.ForeignKey(
        ContactFormSection,
        on_delete=models.CASCADE,
        related_name="points",
        verbose_name="بخش فرم",
        null=True,
        blank=True,
    )
    icon = models.CharField(
        max_length=64,
        verbose_name="آیکون",
        default="message-circle",
        validators=[validate_icon_name],
        help_text=ICON_HELP,
    )
    text = models.CharField(max_length=200, verbose_name="متن")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "مزیت فرم تماس"
        verbose_name_plural = "مزیت‌های فرم تماس"
        ordering = ["order"]

    def __str__(self):
        return self.text


class ContactMapSection(models.Model):
    """بخش «دفتر و پوشش خدمات» — نقشهٔ شعاعیِ دفتر مرکزی"""

    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        blank=True,
        help_text=TITLE_HELP + " مثال: یک دفتر، [[یک تیم متعهد]]",
    )
    subtitle = models.CharField(
        max_length=300, verbose_name="توضیح کوتاه", blank=True
    )
    office_name = models.CharField(
        max_length=100, verbose_name="نام شهرِ دفتر", blank=True, help_text="مثلاً: مشهد"
    )
    office_note = models.CharField(
        max_length=200, verbose_name="توضیح دفتر", blank=True, help_text="مثلاً: دفتر مرکزی و تیم اجرایی"
    )
    coverage_note = models.CharField(
        max_length=200,
        verbose_name="یادداشت پوشش خدمات",
        blank=True,
        help_text="مثلاً: خدمات در سراسر ایران · اجرا و نظارت مستقیم",
    )

    class Meta:
        verbose_name = "بخش نقشهٔ تماس"
        verbose_name_plural = "بخش نقشهٔ تماس"

    def __str__(self):
        return "بخش نقشهٔ تماس"

    def save(self, *args, **kwargs):
        if not self.pk and ContactMapSection.objects.exists():
            raise ValueError("فقط یک سکشن مجاز است")
        super().save(*args, **kwargs)


class ContactFaqSection(models.Model):
    """تنظیمات بخش پرسش‌های پرتکرارِ صفحه تماس"""

    eyebrow = models.CharField(
        max_length=100, verbose_name="متن بالای عنوان", blank=True, help_text=EYEBROW_HELP
    )
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
        blank=True,
        help_text=TITLE_HELP + " مثال: قبل از تماس، [[بدانید]]",
    )
    footer_question = models.CharField(
        max_length=200,
        verbose_name="متن انتهای بخش",
        blank=True,
        help_text="مثلاً: پاسخ‌تان را پیدا نکردید؟",
    )
    footer_cta_text = models.CharField(
        max_length=50, verbose_name="متن دکمهٔ انتهای بخش", blank=True, default="ارسال پیام"
    )

    class Meta:
        verbose_name = "بخش پرسش‌های پرتکرار تماس"
        verbose_name_plural = "بخش پرسش‌های پرتکرار تماس"

    def __str__(self):
        return "بخش پرسش‌های پرتکرار تماس"

    def save(self, *args, **kwargs):
        if not self.pk and ContactFaqSection.objects.exists():
            raise ValueError("فقط یک سکشن مجاز است")
        super().save(*args, **kwargs)


class ContactFaq(models.Model):
    """پرسش و پاسخِ پرتکرارِ صفحه تماس"""

    question = models.CharField(max_length=300, verbose_name="پرسش")
    answer = models.TextField(verbose_name="پاسخ")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "پرسش پرتکرار"
        verbose_name_plural = "پرسش‌های پرتکرار"
        ordering = ["order"]

    def __str__(self):
        return self.question


class SubjectChoice(models.Model):
    """گزینه‌های موضوعِ پیام تماس"""

    label = models.CharField(max_length=100, verbose_name="گزینه")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        verbose_name = "موضوع پیام"
        verbose_name_plural = "موضوع‌های پیام"
        ordering = ["order"]

    def __str__(self):
        return self.label


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
    email = models.EmailField(verbose_name="ایمیل", blank=True)
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    company = models.CharField(
        max_length=200, verbose_name="نام شرکت", blank=True, null=True
    )
    subject = models.CharField(max_length=100, verbose_name="موضوع پیام", blank=True)
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
