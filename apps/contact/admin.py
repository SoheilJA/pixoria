from django.contrib import admin

from apps.core.icon_utils import IconPickerForm

from .models import (
    ContactPageSection,
    ProjectTypeChoice,
    BudgetChoice,
    StartTimeChoice,
    SubjectChoice,
    ContactFormSection,
    ContactFormPoint,
    ContactMapSection,
    ContactFaqSection,
    ContactFaq,
    ContactSubmission,
)


@admin.register(ContactPageSection)
class ContactPageSectionAdmin(admin.ModelAdmin):
    list_display = ["title"]
    fieldsets = [
        (
            "هیرو",
            {
                "fields": ["eyebrow", "title", "description", "response_note"],
                "description": (
                    "کلمه‌ای که در عنوان باید رنگی شود را داخل [[ ]] بنویسید. "
                    "کارت‌های اطلاعات تماس (تلفن، ایمیل، وب‌سایت) از تنظیمات سایت ساخته می‌شوند."
                ),
            },
        ),
    ]

    def has_add_permission(self, request):
        return not ContactPageSection.objects.exists()


class ContactFormPointInline(admin.TabularInline):
    form = IconPickerForm
    model = ContactFormPoint
    extra = 1
    list_editable = ["order"]


@admin.register(ContactFormSection)
class ContactFormSectionAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    fieldsets = [
        (
            "متن",
            {
                "fields": ["eyebrow", "title", "description"],
                "description": "کلمه‌ای که در عنوان باید رنگی شود را داخل [[ ]] بنویسید.",
            },
        ),
        ("دکمه و یادداشت", {"fields": ["button_text", "note"]}),
    ]
    inlines = [ContactFormPointInline]

    def has_add_permission(self, request):
        return not ContactFormSection.objects.exists()


@admin.register(ContactMapSection)
class ContactMapSectionAdmin(admin.ModelAdmin):
    list_display = ["__str__", "office_name"]

    def has_add_permission(self, request):
        return not ContactMapSection.objects.exists()


@admin.register(ContactFaqSection)
class ContactFaqSectionAdmin(admin.ModelAdmin):
    list_display = ["__str__"]

    def has_add_permission(self, request):
        return not ContactFaqSection.objects.exists()


@admin.register(ContactFaq)
class ContactFaqAdmin(admin.ModelAdmin):
    list_display = ["question", "order"]
    list_editable = ["order"]


@admin.register(ProjectTypeChoice)
class ProjectTypeChoiceAdmin(admin.ModelAdmin):
    list_display = ["label", "order"]
    list_editable = ["order"]


@admin.register(BudgetChoice)
class BudgetChoiceAdmin(admin.ModelAdmin):
    list_display = ["label", "order"]
    list_editable = ["order"]


@admin.register(StartTimeChoice)
class StartTimeChoiceAdmin(admin.ModelAdmin):
    list_display = ["label", "order"]
    list_editable = ["order"]


@admin.register(SubjectChoice)
class SubjectChoiceAdmin(admin.ModelAdmin):
    list_display = ["label", "order"]
    list_editable = ["order"]


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "subject", "status", "submitted_at"]
    list_filter = ["status"]
    list_editable = ["status"]
    readonly_fields = [
        "name",
        "email",
        "phone",
        "company",
        "subject",
        "project_type",
        "budget",
        "start_time",
        "message",
        "submitted_at",
    ]
