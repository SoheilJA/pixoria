from django.contrib import admin
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


class ServiceWhyUsInline(admin.TabularInline):
    model = ServiceWhyUs
    extra = 1


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
        "author_name",
        "author_role",
        "author_image",
        "text",
        "order",
        "show_on_home",
    ]
@admin.register(ServiceTestimonial)
class ServiceTestimonialAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'author_role', 'service', 'show_on_home', 'order']
    list_editable = ['show_on_home', 'order']
    list_filter = ['service', 'show_on_home']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["title", "order", "featured"]
    list_editable = ["order", "featured"]
    prepopulated_fields = {"slug": ("title",)}
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
