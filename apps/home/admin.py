from django.contrib import admin
from .models import *


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
