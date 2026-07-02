from django.contrib import admin
from .models import (
    ContactPageSection,
    ContactInfo,
    ProjectTypeChoice,
    BudgetChoice,
    StartTimeChoice,
    ContactSubmission,
)


@admin.register(ContactPageSection)
class ContactPageSectionAdmin(admin.ModelAdmin):
    list_display = ["title"]

    def has_add_permission(self, request):
        return not ContactPageSection.objects.exists()


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ["office_title", "phone", "office_address"]

    def has_add_permission(self, request):
        return not ContactInfo.objects.exists()


@admin.register(ProjectTypeChoice)
class ProjectTypeChoiceAdmin(admin.ModelAdmin):
    list_display = ["label", "order"]


@admin.register(BudgetChoice)
class BudgetChoiceAdmin(admin.ModelAdmin):
    list_display = ["label", "order"]


@admin.register(StartTimeChoice)
class StartTimeChoiceAdmin(admin.ModelAdmin):
    list_display = ["label", "order"]


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "project_type", "status", "submitted_at"]
    list_filter = ["status"]
    list_editable = ["status"]
    readonly_fields = [
        "name",
        "phone",
        "company",
        "project_type",
        "budget",
        "start_time",
        "message",
        "submitted_at",
    ]
