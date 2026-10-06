"""کامپوننتِ بخش نظرات مشتریان.

{% load testimonial_tags %}
{% testimonials_slider %}                              ← نظراتِ صفحهٔ اصلی (show_on_home)
{% testimonials_slider service=object limit=6 %}       ← فقط نظراتِ یک خدمت
{% testimonials_slider title="نظرات" eyebrow="مشتریان" %}

اسلایدر خودش کوئری می‌زند و وقتی نظری وجود ندارد هیچی چاپ نمی‌کند؛ بنابراین
نیازی به پاس‌دادن داده از ویو نیست.
"""

from django import template

from ..models import ServiceTestimonial

register = template.Library()


@register.inclusion_tag("components/testimonials_slider.html")
def testimonials_slider(service=None, limit=9, title="", eyebrow="", id="testimonials"):
    """اسلایدر کارت‌های متنی/ویدیویی/صوتی.

    service: فقط نظراتِ این خدمت (None → نظراتِ عمومیِ صفحهٔ اصلی).
    limit:   حداکثر تعداد کارت.
    title/eyebrow: عنوان و متنِ بالای آن (اختیاری؛ از [[ ]] برای رنگی‌شدن استفاده می‌شود).
    id:      idِ عنصر section (برای لنگرها)."""

    queryset = ServiceTestimonial.objects.filter(service=service) if service else ServiceTestimonial.objects.filter(show_on_home=True)
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 9
    return {
        "testimonials": list(queryset.order_by("order", "id")[:limit]),
        "title": title,
        "eyebrow": eyebrow,
        "section_id": id,
    }
