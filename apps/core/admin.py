from django.contrib import admin
from .models import *


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["site_name", "email", "phone", "status"]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ["label", "name", "url", "order"]


@admin.register(AboutPageHero)
class AboutPageHeroAdmin(admin.ModelAdmin):
    list_display = ["title"]

    def has_add_permission(self, request):
        return not AboutPageHero.objects.exists()


@admin.register(AboutStory)
class AboutStoryAdmin(admin.ModelAdmin):
    list_display = ["__str__"]

    def has_add_permission(self, request):
        return not AboutStory.objects.exists()


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["name", "role", "order"]
    list_editable = ["order"]


@admin.register(AboutValue)
class AboutValueAdmin(admin.ModelAdmin):
    list_display = ["title", "order"]
    list_editable = ["order"]


@admin.register(AboutStat)
class AboutStatAdmin(admin.ModelAdmin):
    list_display = ["label", "number", "order"]
    list_editable = ["order"]


@admin.register(AboutPre)
class AboutPreAdmin(admin.ModelAdmin):
    list_display = ["title", "button_text"]

    def has_add_permission(self, request):
        return not AboutPre.objects.exists()


class ProposalStatInline(admin.TabularInline):
    model = ProposalStat
    extra = 1


class ProposalProblemInline(admin.StackedInline):
    model = ProposalProblem
    extra = 1


class ProposalServiceInline(admin.TabularInline):
    model = ProposalService
    extra = 1


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ["client_name", "client_website", "slug", "created_at"]
    prepopulated_fields = {"slug": ("client_name",)}
    inlines = [ProposalStatInline, ProposalProblemInline, ProposalServiceInline]
