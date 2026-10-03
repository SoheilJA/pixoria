"""Navigation link template tag.

Usage:  {% load nav_tags %}
        <a href="{% nav_url item.url %}">

`nav_url` accepts either a Django URL name ("portfolio:list") or a raw path
("/blog/") and returns the resolved URL, falling back to the input when neither
works — so nav items edited from the admin never render a broken href.
"""

from django import template
from django.urls import NoReverseMatch, reverse

register = template.Library()


@register.simple_tag
def nav_url(value):
    if not value:
        return "/"
    text = str(value).strip()
    if not text:
        return "/"
    try:
        return reverse(text)
    except NoReverseMatch:
        return text
