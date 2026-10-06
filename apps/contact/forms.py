"""فرم تماس صفحهٔ «تماس با ما» — مدل‌فرم روی ContactSubmission.

فیلدها مطابق طرح v2 است: نام، ایمیل، شماره تماس (اختیاری)، موضوع و پیام.
اعتبارسنجی پیام‌های فارسی دارد و یک هانی‌پات (فیلد مخفی «وب‌سایت») را هم
نگه می‌دارد که در ویو چک می‌شود."""

from django import forms
from django.core.exceptions import ValidationError

from .models import ContactSubmission, SubjectChoice


class ContactSubmissionForm(forms.ModelForm):
    # هانی‌پات — برای کاربران مخفی است؛ ربات‌ها آن را پر می‌کنند. در ویو
    # چک می‌شود و هرگز ذخیره نمی‌شود.
    company_website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactSubmission
        fields = ["name", "email", "phone", "subject", "message"]
        error_messages = {
            "name": {"required": "نام و نام خانوادگی را وارد کنید."},
            "email": {"required": "یک ایمیل معتبر وارد کنید."},
            "subject": {"required": "موضوع پیام را انتخاب کنید."},
            "message": {"required": "پیام خود را بنویسید."},
        }
        widgets = {
            "name": forms.TextInput(
                attrs={"autocomplete": "name", "placeholder": " "}
            ),
            "email": forms.EmailInput(
                attrs={
                    "autocomplete": "email",
                    "dir": "ltr",
                    "style": "text-align: right",
                    "placeholder": " ",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "dir": "ltr",
                    "style": "text-align: right",
                    "placeholder": " ",
                }
            ),
            "subject": forms.Select(attrs={}),
            "message": forms.Textarea(attrs={"rows": "5", "placeholder": " "}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # گزینه‌های موضوع از دیتابیس می‌آیند؛ اولین گزینه خالی است تا لیبل
        # شناورِ select در حالت پیش‌فرض نشان داده شود.
        self.fields["subject"].widget.choices = [("", "")] + [
            (choice.label, choice.label) for choice in SubjectChoice.objects.all()
        ]
        # شماره تماس در طرح v2 اختیاری است.
        self.fields["phone"].required = False

    def clean_subject(self):
        """موضوع باید یکی از گزینه‌های دیتابیس باشد تا هرزنامه‌ها رد شوند."""
        value = self.cleaned_data.get("subject", "").strip()
        if value and not SubjectChoice.objects.filter(label=value).exists():
            raise ValidationError("موضوع پیام را از فهرست انتخاب کنید.")
        return value

    def clean(self):
        super().clean()
        # متن کوتاه پیام مزخرف است؛ طول حداقل مثل فرم تماس سریع نگه داشته شد.
        message = self.cleaned_data.get("message", "")
        if message and len(message) < 10:
            self.add_error(
                "message", "پیام را کمی طولانی‌تر بنویسید (حداقل ۱۰ نویسه)."
            )
        return self.cleaned_data
