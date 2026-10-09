from django.contrib import admin

from apps.core.icon_utils import IconPickerForm, IconPreviewMixin
from .models import (
    Category,
    Portfolio,
    PortfolioPageSection,
    ProjectImage,
    ProjectStat,
)


@admin.register(PortfolioPageSection)
class PortfolioPageSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "eyebrow"]

    def has_add_permission(self, request):
        return not PortfolioPageSection.objects.exists()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order"]
    prepopulated_fields = {"slug": ("name",)}


class ProjectStatInline(IconPreviewMixin, admin.TabularInline):
    form = IconPickerForm
    model = ProjectStat
    extra = 1
    fields = ["icon_preview", "icon", "number", "label", "description", "order"]
    readonly_fields = ["icon_preview"]
    ordering = ["order"]


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ["title", "client_name", "service", "year", "featured", "order"]
    list_editable = ["featured", "order"]
    list_filter = ["categories", "service", "featured"]
    search_fields = ["title", "client_name"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["categories"]
    inlines = [ProjectStatInline, ProjectImageInline]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "title",
                    "slug",
                    "excerpt",
                    "description",
                ]
            },
        ),
        (
            "تصویر و گالری",
            {
                "fields": ["image", "image_alt"],
                "description": "تصاویر بیشتر در بخش گالری (پایین صفحه) اضافه می‌شوند.",
            },
        ),
        (
            "مشتری و دسته‌بندی",
            {
                "fields": [
                    "client_name",
                    "year",
                    "service",
                    "service_type",
                    "client_url",
                    "categories",
                ]
            },
        ),
        (
            "محتوای پروژه",
            {"fields": ["challenge", "solution", "technologies"]},
        ),
        (
            "بازخورد و سئو",
            {
                "fields": ["testimonial", "meta_description"],
                "description": "اختیاری — همهٔ این فیلدها خالی هم کار می‌کنند.",
            },
        ),
        (
            "نمایش",
            {"fields": ["featured", "order"]},
        ),
    ]
