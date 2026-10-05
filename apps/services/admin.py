from django.contrib import admin

from apps.core.icon_utils import IconPreviewMixin
from .models import (
    ServicesPageSection,
    Service,
    ServiceStat,
    ServiceWhyUs,
    ServiceDeliverable,
    ServiceProcess,
    ServicePlan,
    ServicePlanFeature,
    ServiceCustomItem,
    ServiceFAQ,
    ServiceTestimonial,
)


@admin.register(ServicesPageSection)
class ServicesPageSectionAdmin(admin.ModelAdmin):
    list_display = ["title"]

    def has_add_permission(self, request):
        return not ServicesPageSection.objects.exists()


class ServiceStatInline(admin.TabularInline):
    model = ServiceStat
    extra = 1


class ServiceWhyUsInline(IconPreviewMixin, admin.TabularInline):
    model = ServiceWhyUs
    extra = 1
    fields = ["icon_preview", "icon", "title", "description", "order"]
    readonly_fields = ["icon_preview"]


class ServiceDeliverableInline(admin.TabularInline):
    model = ServiceDeliverable
    extra = 1


class ServiceProcessInline(admin.TabularInline):
    model = ServiceProcess
    extra = 1


class ServicePlanFeatureInline(admin.TabularInline):
    model = ServicePlanFeature
    extra = 1


class ServicePlanInline(admin.StackedInline):
    model = ServicePlan
    extra = 1
    show_change_link = True


class ServiceCustomItemInline(admin.TabularInline):
    model = ServiceCustomItem
    extra = 1


class ServiceFAQInline(admin.TabularInline):
    model = ServiceFAQ
    extra = 1


class ServiceTestimonialInline(admin.TabularInline):
    model = ServiceTestimonial
    extra = 1
    fields = [
        "kind",
        "author_name",
        "author_role",
        "author_image",
        "text",
        "rating",
        "order",
        "show_on_home",
    ]


@admin.register(ServiceTestimonial)
class ServiceTestimonialAdmin(admin.ModelAdmin):
    list_display = ["author_name", "author_role", "kind", "service", "show_on_home", "order"]
    list_editable = ["show_on_home", "order"]
    list_filter = ["service", "show_on_home", "kind"]
    search_fields = ["author_name", "author_role", "text"]


@admin.register(Service)
class ServiceAdmin(IconPreviewMixin, admin.ModelAdmin):
    list_display = ["icon_preview", "title", "visual", "card_span", "order", "featured"]
    list_editable = ["visual", "card_span", "order", "featured"]
    list_display_links = ["icon_preview", "title"]
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = [
        ("هویت خدمت", {"fields": ["title", "slug", "icon", "excerpt", "description"]}),
        (
            "کارت صفحه اصلی",
            {"fields": ["visual", "card_span", "chips", "badge", "featured", "order"]},
        ),
        ("تگ‌ها", {"fields": ["tags"]}),
    ]
    inlines = [
        ServiceStatInline,
        ServiceWhyUsInline,
        ServiceDeliverableInline,
        ServiceProcessInline,
        ServicePlanInline,
        ServiceCustomItemInline,
        ServiceFAQInline,
        ServiceTestimonialInline,
    ]


@admin.register(ServicePlan)
class ServicePlanAdmin(admin.ModelAdmin):
    list_display = ["service", "name", "plan_type", "price", "is_featured"]
    inlines = [ServicePlanFeatureInline]
