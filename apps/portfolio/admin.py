from django.contrib import admin
from .models import *



@admin.register(PortfolioPageSection)
class PortfolioPageSectionAdmin(admin.ModelAdmin):
    list_display=['title']

    def has_add_permission(self, request):
        return not PortfolioPageSection.objects.exists()

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order"]
    prepopulated_fields = {"slug": ("name",)}


class ProjectStatInline(admin.TabularInline):
    model = ProjectStat
    extra = 1


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ["title", "client_name", "year", "featured", "order"]
    list_editable = ["featured", "order"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["categories"]
    inlines = [ProjectStatInline]
