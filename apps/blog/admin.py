from django.contrib import admin
from .models import Category, Article, Tag, Author, BlogPageSettings


@admin.register(BlogPageSettings)
class BlogPageSettingsAdmin(admin.ModelAdmin):
    list_display = ["title"]

    def has_add_permission(self, request):
        return not BlogPageSettings.objects.exists()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["title"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name", "role"]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "status", "published_at", "reading_time"]
    list_filter = ["status", "category"]
    search_fields = ["title", "excerpt"]

    fieldsets = (
        (
            "محتوای اصلی",
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "cover_image",
                    "cover_image_alt",
                    "excerpt",
                    "content",
                ),
            },
        ),
        (
            "انتشار",
            {
                "fields": ("status", "published_at"),
            },
        ),
        (
            "سئو",
            {
                "fields": ("meta_title", "meta_description"),
                "description": "در صورت خالی گذاشتن، از عنوان و خلاصه مقاله استفاده می‌شود.",
            },
        ),
    )
