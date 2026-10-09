"""کامپوننتِ کاروسل نمونه‌کارها.

{% load projects_tags %}
{% projects_carousel %}                                  ← همهٔ نمونه‌کارها
{% projects_carousel exclude=project %}                  ← نمونه‌کارهای مرتبط
{% projects_carousel category=category limit=6 %}        ← نمونه‌کارهای یک دسته‌بندی
{% projects_carousel service=service limit=6 %}          ← نمونه‌کارهای یک خدمت

کاروسل خودش کوئری می‌زند و وقتی نمونه‌کاری نیست چیزی چاپ نمی‌کند.
"""

from django import template
from django.db.models import Q

from ..models import Portfolio

register = template.Library()


@register.inclusion_tag("components/projects_carousel.html")
def projects_carousel(exclude=None, category=None, service=None, limit=8):
    """کاروسل کارت‌های نمونه‌کار.

    exclude:  نمونه‌کاری که نباید نمایش داده شود (نمونهٔ Portfolio؛ مثلاً پروژهٔ فعلی).
    category: دسته‌بندی برای فیلتر (نمونهٔ Category یا اسلاگ)؛ None → همهٔ دسته‌ها.
    service:  خدمت برای فیلتر (نمونهٔ Service یا عنوانِ آن به‌صورتِ رشته). ابتدا از
              ارتباطِ واقعیِ `Portfolio.service` استفاده می‌شود و فیلدِ متنیِ
              `service_type` به‌عنوان fallback کنارش می‌ماند.
    limit:    حداکثر تعداد کارت."""

    queryset = Portfolio.objects.all()
    if exclude is not None:
        queryset = queryset.exclude(pk=exclude.pk)
    if category is not None:
        slug = category.slug if hasattr(category, "slug") else category
        queryset = queryset.filter(categories__slug=slug)
    if service is not None:
        # یک رشتهٔ آزاد فقط روی فیلدِ متنی تطابق می‌خورد (FK به یک Service
        # واقعی نیاز دارد). نمونهٔ Service هم «title» دارد، بنابراین hasattr
        # اینجا کار درستی نمی‌کند.
        if isinstance(service, str):
            queryset = queryset.filter(service_type=service)
        else:
            # ابتدا ارتباطِ واقعیِ Portfolio.service، و فیلدِ متنیِ service_type
            # به‌عنوانِ fallback کنارش نگه داشته شده (T61).
            queryset = queryset.filter(
                Q(service=service) | Q(service_type=service.title)
            ).distinct()
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 8
    return {
        "projects": list(queryset.order_by("order", "id")[:limit]),
    }
