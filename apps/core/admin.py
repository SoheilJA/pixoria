from django.contrib import admin
from django import forms

from .brand_utils import BrandChoiceWidget
from .icon_utils import IconPickerForm, IconPreviewMixin
from .models import *


class SiteSettingsForm(forms.ModelForm):
    """فرم تنظیمات سایت — انتخاب برند با ویجتِ پیش‌نمایش‌دار (T58)."""

    class Meta:
        model = SiteSettings
        fields = "__all__"
        widgets = {
            "logo_choice": BrandChoiceWidget,
            "favicon_choice": BrandChoiceWidget,
        }


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsForm
    list_display = ["site_name", "email", "phone", "status"]
    fieldsets = [
        (
            "مشخصات سایت",
            {
                "fields": [
                    "site_name",
                    "site_description",
                    "established_year",
                    "status",
                    "logo",
                    "logo_choice",
                    "favicon",
                    "favicon_choice",
                    "apple_touch_icon",
                    "og_image",
                ],
                "description": (
                    "فایل‌های آپلودشده روی گزینه‌های پیش‌فرض اولویت دارند. "
                    "گزینهٔ پیش‌فرض فقط تا زمانی که فایل آپلود نشده استفاده می‌شود."
                ),
            },
        ),
        (
            "اطلاعات تماس",
            {
                "fields": [
                    "email",
                    "phone",
                    "phone_label",
                    "phone_secondary",
                    "phone_secondary_label",
                    "address",
                    "website",
                ]
            },
        ),
        (
            "فوتر",
            {
                "fields": [
                    "footer_description",
                    "tagline",
                    "trust_first_title",
                    "trust_first_subtitle",
                    "trust_second_title",
                    "trust_second_subtitle",
                    "trust_note",
                ]
            },
        ),
        (
            "مگامنوی خدمات (هدر)",
            {
                "fields": ["mega_title", "mega_description", "mega_cta_text"],
                "description": "بنر بالای منوی کشویی خدمات در هدر سایت.",
            },
        ),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    form = IconPickerForm
    list_display = ["label", "name", "icon", "url", "order"]
    list_editable = ["order"]


class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 1
    list_editable = ["order"]


@admin.register(FooterLinkGroup)
class FooterLinkGroupAdmin(admin.ModelAdmin):
    list_display = ["title", "order", "is_active"]
    list_editable = ["order", "is_active"]
    inlines = [FooterLinkInline]


@admin.register(AboutPageHero)
class AboutPageHeroAdmin(admin.ModelAdmin):
    list_display = ["title"]
    fieldsets = [
        (
            "محتوای اصلی",
            {
                "fields": [
                    "eyebrow",
                    "title",
                    "description",
                ]
            },
        ),
        (
            "دکمه‌ها",
            {
                "fields": [
                    "cta_primary_text",
                    "cta_primary_url",
                    "cta_secondary_text",
                    "cta_secondary_url",
                ],
                "description": (
                    "دکمهٔ دوم وقتی لینکش خالی باشد نمایش داده نمی‌شود. "
                    "مدارِ خدمات کنار هیرو از لیست خدمات دیتابیس ساخته می‌شود."
                ),
            },
        ),
    ]

    def has_add_permission(self, request):
        return not AboutPageHero.objects.exists()


@admin.register(AboutStory)
class AboutStoryAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    fieldsets = [
        (
            "سرتیتر",
            {
                "fields": ["eyebrow", "title"],
                "description": (
                    "کلمه‌ای که در عنوان باید رنگی شود را داخل [[ ]] بنویسید."
                ),
            },
        ),
        ("متن", {"fields": ["description", "body", "chips", "quote"]}),
        (
            "تصویر",
            {
                "fields": ["image", "image_alt", "image_caption"],
                "description": "تصویر اختیاری است؛ بدون تصویر فقط متن داستان نشان داده می‌شود.",
            },
        ),
    ]

    def has_add_permission(self, request):
        return not AboutStory.objects.exists()


@admin.register(AboutJourneySection)
class AboutJourneySectionAdmin(admin.ModelAdmin):
    form = IconPickerForm
    list_display = ["__str__", "badge_text"]

    def has_add_permission(self, request):
        return not AboutJourneySection.objects.exists()


@admin.register(AboutJourneyStep)
class AboutJourneyStepAdmin(admin.ModelAdmin):
    list_display = ["year", "title", "subtitle", "order"]
    list_editable = ["order"]


@admin.register(AboutClientsSection)
class AboutClientsSectionAdmin(admin.ModelAdmin):
    list_display = ["__str__"]

    def has_add_permission(self, request):
        return not AboutClientsSection.objects.exists()


@admin.register(AboutStat)
class AboutStatAdmin(IconPreviewMixin, admin.ModelAdmin):
    form = IconPickerForm
    list_display = ["label", "icon_preview", "value", "prefix", "suffix", "order"]
    list_editable = ["order"]
    fieldsets = [
        (
            "عدد شمارش‌شونده",
            {
                "fields": ["value", "prefix", "suffix"],
                "description": (
                    "این فیلدها در طرح v2 نمایش داده می‌شوند: «پیشوند مقدار پسوند» "
                    "که با انیمیشن می‌شمارند. فیلد قدیمیِ «متن عدد» فقط برای "
                    "قالب‌های قدیمی باقی مانده است."
                ),
            },
        ),
        ("متن", {"fields": ["label", "description"]}),
        ("نمایش", {"fields": ["icon"]}),
    ]
