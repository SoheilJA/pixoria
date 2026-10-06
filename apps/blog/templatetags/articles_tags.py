"""کامپوننتِ کاروسل مقالات.

{% load articles_tags %}
{% articles_carousel %}                                     ← آخرین مقالات منتشرشده
{% articles_carousel exclude=article %}                     ← مقالات مرتبط (جز مقالهٔ فعلی)
{% articles_carousel category=article.category limit=4 %}   ← مقالات یک دسته‌بندی

کاروسل خودش کوئری می‌زند و وقتی مقاله‌ای نیست چیزی چاپ نمی‌کند.
"""

from django import template
from django.utils import timezone

from ..models import Article

register = template.Library()


@register.inclusion_tag("components/articles_carousel.html")
def articles_carousel(exclude=None, category=None, limit=8):
    """کاروسل کارت‌های مقاله.

    exclude:  مقاله‌ای که نباید نمایش داده شود (نمونهٔ Article؛ مثلاً مقالهٔ فعلی).
    category: دسته‌بندی برای فیلتر (نمونهٔ Category یا اسلاگ)؛ None → همهٔ دسته‌ها.
    limit:    حداکثر تعداد کارت."""

    queryset = Article.objects.filter(
        status="published", published_at__lte=timezone.now()
    )
    if exclude is not None:
        queryset = queryset.exclude(pk=exclude.pk)
    if category is not None:
        slug = category.slug if hasattr(category, "slug") else category
        queryset = queryset.filter(category__slug=slug)
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 8
    return {
        "articles": list(queryset.order_by("-published_at", "-id")[:limit]),
    }
