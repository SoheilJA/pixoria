from django.contrib import admin

from apps.core.icon_utils import IconPickerForm, IconPreviewMixin
from .models import *


class PackageFeatureInline(admin.TabularInline):
    model = PackageFeature
    extra = 1
    ordering = ["order"]


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ["title"]
    fields = [
        "eyebrow",
        "title",
        "description",
        "cta_primary_text",
        "cta_primary_url",
        "cta_secondary_text",
        "cta_secondary_url",
    ]

    def has_add_permission(self, request):
        return not HeroSection.objects.exists()


@admin.register(HeroStat)
class HeroStatAdmin(IconPreviewMixin, admin.ModelAdmin):
    form = IconPickerForm
    list_display = ["icon_preview", "value", "label", "icon", "order", "is_active"]
    list_editable = ["value", "label", "icon", "order", "is_active"]
    list_display_links = ["icon_preview"]


@admin.register(HeroMarqueeItem)
class HeroMarqueeItemAdmin(admin.ModelAdmin):
    list_display = ["text", "order"]


class HomeAboutStatInline(IconPreviewMixin, admin.TabularInline):
    form = IconPickerForm
    model = HomeAboutStat
    extra = 1
    fields = ["icon_preview", "icon", "value", "prefix", "suffix", "label", "order", "is_active"]
    readonly_fields = ["icon_preview"]
    ordering = ["order"]


@admin.register(HomeAboutSection)
class HomeAboutSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "eyebrow"]
    fields = ["eyebrow", "title", "paragraph_one", "paragraph_two", "chips", "footer_label"]
    inlines = [HomeAboutStatInline]

    def has_add_permission(self, request):
        return not HomeAboutSection.objects.exists()


@admin.register(HomeAboutStat)
class HomeAboutStatAdmin(IconPreviewMixin, admin.ModelAdmin):
    form = IconPickerForm
    list_display = ["icon_preview", "label", "value", "prefix", "suffix", "icon", "order", "is_active"]
    list_editable = ["value", "prefix", "suffix", "icon", "order", "is_active"]
    list_display_links = ["icon_preview", "label"]


@admin.register(TrustedSection)
class TrustedSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "eyebrow"]
    fields = ["eyebrow", "title", "description", "footer_label"]

    def has_add_permission(self, request):
        return not TrustedSection.objects.exists()


@admin.register(TestimonialSection)
class TestimonialSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "eyebrow"]
    fields = ["eyebrow", "title", "description"]

    def has_add_permission(self, request):
        return not TestimonialSection.objects.exists()


@admin.register(FeaturedWorkSection)
class FeaturedWorkSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "eyebrow"]

    def has_add_permission(self, request):
        return not FeaturedWorkSection.objects.exists()


@admin.register(ServicesSection)
class ServicesSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "eyebrow"]

    def has_add_permission(self, request):
        return not ServicesSection.objects.exists()


@admin.register(ClientMarqueeItem)
class ClientMarqueeItemAdmin(admin.ModelAdmin):
    list_display = ["name", "mark", "accent", "order"]
    list_editable = ["mark", "accent", "order"]
    list_display_links = ["name"]


@admin.register(ManifestoSection)
class ManifestoSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "label"]

    def has_add_permission(self, request):
        return not ManifestoSection.objects.exists()


@admin.register(CTASection)
class CTASectionAdmin(admin.ModelAdmin):
    list_display = ["title", "eyebrow", "email", "phone"]
    fields = ["eyebrow", "title", "description", "email", "phone"]

    def has_add_permission(self, request):
        return not CTASection.objects.exists()


@admin.register(LatestArticlesSection)
class LatestArticlesSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "eyebrow", "subtitle"]

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
    list_display = ["title", "eyebrow", "subtitle"]

    def has_add_permission(self, request):
        return not StatsSection.objects.exists()


@admin.register(StatItem)
class StatItemAdmin(IconPreviewMixin, admin.ModelAdmin):
    form = IconPickerForm
    list_display = ["icon_preview", "label", "value", "prefix", "suffix", "icon", "order", "is_active"]
    list_editable = ["value", "prefix", "suffix", "icon", "order", "is_active"]
    list_display_links = ["icon_preview", "label"]


@admin.register(ProcessSection)
class ProcessSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "eyebrow", "subtitle"]

    def has_add_permission(self, request):
        return not ProcessSection.objects.exists()


@admin.register(ProcessStep)
class ProcessStepAdmin(IconPreviewMixin, admin.ModelAdmin):
    form = IconPickerForm
    list_display = ["icon_preview", "title", "icon", "order", "is_active"]
    list_editable = ["icon", "order", "is_active"]
    list_display_links = ["icon_preview", "title"]


@admin.register(WhySection)
class WhySectionAdmin(admin.ModelAdmin):
    list_display = ["title", "eyebrow", "subtitle"]

    def has_add_permission(self, request):
        return not WhySection.objects.exists()


@admin.register(WhyFeature)
class WhyFeatureAdmin(admin.ModelAdmin):
    form = IconPickerForm
    list_display = ["title", "icon", "size", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_display_links = ["title"]
    search_fields = ["title"]


@admin.register(TechSection)
class TechSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "eyebrow", "subtitle"]

    def has_add_permission(self, request):
        return not TechSection.objects.exists()


@admin.register(TechSkill)
class TechSkillAdmin(IconPreviewMixin, admin.ModelAdmin):
    form = IconPickerForm
    list_display = ["icon_preview", "name", "icon", "level", "category", "order", "is_active"]
    list_editable = ["icon", "level", "order", "is_active"]
    list_display_links = ["icon_preview", "name"]
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
    list_display = ["title", "eyebrow", "subtitle"]

    def has_add_permission(self, request):
        return not FaqSection.objects.exists()


@admin.register(FaqItem)
class FaqItemAdmin(admin.ModelAdmin):
    list_display = ["question", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_display_links = ["question"]
    search_fields = ["question"]
