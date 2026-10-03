from django.contrib import admin
from .models import *


class PackageFeatureInline(admin.TabularInline):
    model = PackageFeature
    extra = 1
    ordering = ["order"]


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ["title"]

    def has_add_permission(self, request):
        return not HeroSection.objects.exists()


@admin.register(HeroMarqueeItem)
class HeroMarqueeItemAdmin(admin.ModelAdmin):
    list_display = ["text", "order"]


@admin.register(FeaturedWorkSection)
class FeaturedWorkSectionAdmin(admin.ModelAdmin):
    list_display = ["title"]

    def has_add_permission(self, request):
        return not FeaturedWorkSection.objects.exists()


@admin.register(ServicesSection)
class ServicesSectionAdmin(admin.ModelAdmin):
    list_display = ["title"]

    def has_add_permission(self, request):
        return not ServicesSection.objects.exists()


@admin.register(ClientMarqueeItem)
class ClientMarqueeItemAdmin(admin.ModelAdmin):
    list_display = ["name", "order"]


@admin.register(ManifestoSection)
class ManifestoSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "label"]

    def has_add_permission(self, request):
        return not ManifestoSection.objects.exists()


@admin.register(CTASection)
class CTASectionAdmin(admin.ModelAdmin):
    list_display = ["title", "email", "phone"]

    def has_add_permission(self, request):
        return not CTASection.objects.exists()


@admin.register(LatestArticlesSection)
class LatestArticlesSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "subtitle"]

    def has_add_permission(self, request):
        return not LatestArticlesSection.objects.exists()


@admin.register(HeaderSettings)
class HeaderSettingsAdmin(admin.ModelAdmin):
    list_display = ["cta_text", "cta_url", "show_cta"]

    def has_add_permission(self, request):
        return not HeaderSettings.objects.exists()


@admin.register(NavItem)
class NavItemAdmin(admin.ModelAdmin):
    list_display = ["title", "url", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_display_links = ["title"]
    search_fields = ["title", "url"]


@admin.register(HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "key", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_display_links = ["title"]


@admin.register(StatsSection)
class StatsSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "subtitle"]

    def has_add_permission(self, request):
        return not StatsSection.objects.exists()


@admin.register(StatItem)
class StatItemAdmin(admin.ModelAdmin):
    list_display = ["label", "value", "prefix", "suffix", "order", "is_active"]
    list_editable = ["value", "prefix", "suffix", "order", "is_active"]
    list_display_links = ["label"]


@admin.register(ProcessSection)
class ProcessSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "subtitle"]

    def has_add_permission(self, request):
        return not ProcessSection.objects.exists()


@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ["title", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_display_links = ["title"]


@admin.register(WhySection)
class WhySectionAdmin(admin.ModelAdmin):
    list_display = ["title", "subtitle"]

    def has_add_permission(self, request):
        return not WhySection.objects.exists()


@admin.register(WhyFeature)
class WhyFeatureAdmin(admin.ModelAdmin):
    list_display = ["title", "icon", "size", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_display_links = ["title"]
    search_fields = ["title"]


@admin.register(TechSection)
class TechSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "subtitle"]

    def has_add_permission(self, request):
        return not TechSection.objects.exists()


@admin.register(TechSkill)
class TechSkillAdmin(admin.ModelAdmin):
    list_display = ["name", "level", "category", "order", "is_active"]
    list_editable = ["level", "order", "is_active"]
    list_display_links = ["name"]
    search_fields = ["name", "category"]


@admin.register(PackagesSection)
class PackagesSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "subtitle"]

    def has_add_permission(self, request):
        return not PackagesSection.objects.exists()


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "is_featured", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_display_links = ["name"]
    inlines = [PackageFeatureInline]


@admin.register(FaqSection)
class FaqSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "subtitle"]

    def has_add_permission(self, request):
        return not FaqSection.objects.exists()


@admin.register(FaqItem)
class FaqItemAdmin(admin.ModelAdmin):
    list_display = ["question", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_display_links = ["question"]
    search_fields = ["question"]


@admin.register(ContactSection)
class ContactSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "subtitle", "submit_text"]

    def has_add_permission(self, request):
        return not ContactSection.objects.exists()
