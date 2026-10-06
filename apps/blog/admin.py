from django.contrib import admin
from .models import Category, Article, Tag, Author, BlogPageSettings


@admin.register(BlogPageSettings)
class BlogPageSettingsAdmin(admin.ModelAdmin):
    list_display = ["title"]
    fieldsets = (
        (
            None,
            {
                "fields": ("eyebrow", "title", "description"),
                "description": "عنوان از طریق مارکر [[ ]] کلمهٔ رنگی می‌گیرد.",
            },
        ),
    )

    def has_add_permission(self, request):
        return not BlogPageSettings.objects.exists()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["title"]
    search_fields = ["title"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name", "role"]
    search_fields = ["name"]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "status",
        "featured",
        "published_at",
        "reading_time",
    ]
    list_filter = ["status", "featured", "category", "author"]
    list_editable = ["status", "featured"]
    search_fields = ["title", "excerpt", "meta_title"]
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        (
            "محتوای اصلی",
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "tags",
                    "author",
                    "cover_image",
                    "cover_image_alt",
                    "excerpt",
                    "content",
                )
            },
        ),
        (
            "انتشار",
            {
                "fields": ("status", "featured", "published_at"),
                "description": "فقط یک مقالهٔ ویژه در اسلات بالای صفحهٔ بلاگ جای می‌گیرد.",
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
