from django.contrib import admin

from apps.core.icon_utils import IconPickerForm, IconPreviewMixin
from .models import (
    ServicesPageSection,
    ServicesHowSection,
    ServicesHowStep,
    Service,
    ServiceSection,
    ServiceTool,
    ServiceUseCase,
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
    fields = ["eyebrow", "title", "description"]

    def has_add_permission(self, request):
        return not ServicesPageSection.objects.exists()


class ServicesHowStepInline(IconPreviewMixin, admin.TabularInline):
    model = ServicesHowStep
    extra = 1
    form = IconPickerForm
    fields = ["icon", "title", "description", "order"]


@admin.register(ServicesHowSection)
class ServicesHowSectionAdmin(admin.ModelAdmin):
    list_display = ["title"]
    fields = ["eyebrow", "title", "subtitle"]
    inlines = [ServicesHowStepInline]

    def has_add_permission(self, request):
        return not ServicesHowSection.objects.exists()


class ServiceStatInline(admin.TabularInline):
    model = ServiceStat
    extra = 1


class ServiceSectionInline(admin.StackedInline):
    """بخش‌های محتوای بلند — Stacked چون body یک rich-text است."""

    model = ServiceSection
    extra = 1
    fields = ["eyebrow", "title", "body", "image", "image_alt", "layout", "order", "is_active"]
    ordering = ["order"]


class ServiceToolInline(IconPreviewMixin, admin.TabularInline):
    form = IconPickerForm
    model = ServiceTool
    extra = 1
    fields = ["icon_preview", "icon", "name", "order"]
    readonly_fields = ["icon_preview"]
    ordering = ["order"]


class ServiceUseCaseInline(IconPreviewMixin, admin.TabularInline):
    form = IconPickerForm
    model = ServiceUseCase
    extra = 1
    fields = ["icon_preview", "icon", "title", "description", "order"]
    readonly_fields = ["icon_preview"]
    ordering = ["order"]


class ServiceWhyUsInline(IconPreviewMixin, admin.TabularInline):
    form = IconPickerForm
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
    """دقیقاً سه پلن برای هر خدمت — max_num/validationِ «یک پلنِ پیشنهادی»
    در مدل است (ServicePlan.clean)."""

    model = ServicePlan
    extra = 3
    max_num = 3
    show_change_link = True
    fields = [
        "plan_type",
        "name",
        "tagline",
        "price",
        "price_prefix",
        "price_currency",
        "price_note",
        "old_price",
        "discount_label",
        "cta_label",
        "cta_url",
        "is_featured",
        "is_active",
        "order",
    ]


class ServiceCustomItemInline(admin.TabularInline):
    model = ServiceCustomItem
    extra = 1


class ServiceFAQInline(admin.TabularInline):
    model = ServiceFAQ
    extra = 1


class ServiceTestimonialInline(admin.TabularInline):
    model = ServiceTestimonial
    extra = 1
    # همهٔ فیلدها اینجا هستند تا کارت‌های ویدیویی/صوتی هم از داخلِ صفحهٔ خدمت
    # قابل ساخت باشند؛ testimonial_kind.js ردیفِ هر فیلد را بر اساس نوع مخفی می‌کند.
    fields = [
        "kind",
        "author_name",
        "author_role",
        "author_image",
        "text",
        "video_file",
        "video_url",
        "video_poster",
        "video_duration",
        "audio_file",
        "audio_url",
        "audio_title",
        "audio_project",
        "audio_duration",
        "rating",
        "order",
        "show_on_home",
    ]

    class Media:
        js = ["admin/js/testimonial_kind.js"]


@admin.register(ServiceTestimonial)
class ServiceTestimonialAdmin(admin.ModelAdmin):
    list_display = ["author_name", "author_role", "kind", "service", "show_on_home", "order"]
    list_editable = ["show_on_home", "order"]
    list_filter = ["service", "show_on_home", "kind"]
    search_fields = ["author_name", "author_role", "text"]
    fieldsets = [
        (
            "مشترک",
            {
                "fields": [
                    "kind",
                    "service",
                    "author_name",
                    "author_role",
                    "author_image",
                    "rating",
                    "show_on_home",
                    "order",
                ]
            },
        ),
        ("متن نظر", {"fields": ["text"], "classes": ["kind-text"]}),
        (
            "ویدیو",
            {
                "fields": ["video_file", "video_url", "video_poster", "video_duration"],
                "classes": ["kind-video"],
            },
        ),
        (
            "صوت",
            {
                "fields": [
                    "audio_file",
                    "audio_url",
                    "audio_title",
                    "audio_project",
                    "audio_duration",
                ],
                "classes": ["kind-audio"],
            },
        ),
    ]

    class Media:
        js = ["admin/js/testimonial_kind.js"]


@admin.register(Service)
class ServiceAdmin(IconPreviewMixin, admin.ModelAdmin):
    form = IconPickerForm
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
        (
            "صفحهٔ اختصاصی — تم",
            {
                "fields": ["accent"],
                "description": (
                    "رنگِ لهجهٔ صفحهٔ اختصاصیِ این خدمت (حلقه‌ها، سیاره و خطوط)."
                ),
            },
        ),
        (
            "صفحهٔ اختصاصی — هیرو",
            {
                "fields": [
                    "hero_eyebrow",
                    "hero_title",
                    "hero_lead",
                    "hero_cta_primary_text",
                    "hero_cta_primary_url",
                    "hero_cta_secondary_text",
                    "hero_cta_secondary_url",
                ],
                "description": (
                    "همهٔ این فیلدها اختیاری هستند؛ خالی → از عنوان و توضیحات کوتاه "
                    "استفاده می‌شود. عنوانِ خالی → h1 همان «عنوان» بالاست. "
                    "لینکِ دکمهٔ دومِ خالی → دکمه نشان داده نمی‌شود."
                ),
            },
        ),
        (
            "صفحهٔ اختصاصی — خدمات مرتبط",
            {
                "fields": ["related_services"],
                "description": "کارتِ خدماتِ مرتبط پایینِ صفحهٔ اختصاصی.",
            },
        ),
        (
            "سئو",
            {
                "fields": ["meta_title", "meta_description", "og_image"],
                "description": (
                    "در صورت خالی گذاشتن، از عنوان/توضیحات کوتاه و لوگوی سایت "
                    "استفاده می‌شود."
                ),
            },
        ),
    ]
    inlines = [
        ServiceSectionInline,
        ServiceStatInline,
        ServiceWhyUsInline,
        ServiceDeliverableInline,
        ServiceProcessInline,
        ServiceToolInline,
        ServiceUseCaseInline,
        ServicePlanInline,
        ServiceCustomItemInline,
        ServiceFAQInline,
        ServiceTestimonialInline,
    ]


@admin.register(ServicePlan)
class ServicePlanAdmin(admin.ModelAdmin):
    list_display = ["service", "name", "plan_type", "price", "is_featured"]
    inlines = [ServicePlanFeatureInline]
