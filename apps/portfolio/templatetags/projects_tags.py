"""کامپوننتِ کاروسل نمونه‌کارها.

{% load projects_tags %}
{% projects_carousel %}                                  ← همهٔ نمونه‌کارها
{% projects_carousel exclude=project %}                  ← نمونه‌کارهای مرتبط
{% projects_carousel category=category limit=6 %}        ← نمونه‌کارهای یک دسته‌بندی
{% projects_carousel service=service limit=6 %}          ← نمونه‌کارهای یک حوزهٔ کاری

کاروسل خودش کوئری می‌زند و وقتی نمونه‌کاری نیست چیزی چاپ نمی‌کند.
"""

from django import template

from ..models import Portfolio

register = template.Library()


@register.inclusion_tag("components/projects_carousel.html")
def projects_carousel(exclude=None, category=None, service=None, limit=8):
    """کاروسل کارت‌های نمونه‌کار.

    exclude:  نمونه‌کاری که نباید نمایش داده شود (نمونهٔ Portfolio؛ مثلاً پروژهٔ فعلی).
    category: دسته‌بندی برای فیلتر (نمونهٔ Category یا اسلاگ)؛ None → همهٔ دسته‌ها.
    service:  حوزهٔ کاری برای فیلتر (نمونهٔ Service → از title آن، یا رشتهٔ آزاد)؛
              Portfolio به Service متصل نیست، فقط فیلد متنی service_type را دارد.
    limit:    حداکثر تعداد کارت."""

    queryset = Portfolio.objects.all()
    if exclude is not None:
        queryset = queryset.exclude(pk=exclude.pk)
    if category is not None:
        slug = category.slug if hasattr(category, "slug") else category
        queryset = queryset.filter(categories__slug=slug)
    if service is not None:
        # یک رشته مستقیماً استفاده می‌شود؛ نمونهٔ Service از title آن. (str خودش
        # متدی به نام title دارد، بنابراین hasattr در اینجا کار درستی نمی‌کند.)
        title = service if isinstance(service, str) else service.title
        queryset = queryset.filter(service_type=title)
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 8
    return {
        "projects": list(queryset.order_by("order", "id")[:limit]),
    }
