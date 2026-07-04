from django.shortcuts import render
from .models import (
    HeroSection,
    HeroMarqueeItem,
    FeaturedWorkSection,
    ServicesSection,
    ClientMarqueeItem,
    ManifestoSection,
    CTASection,
)
from apps.portfolio.models import Portfolio


def home(request):
    context = {
        "hero": HeroSection.objects.first(),
        "hero_marquee": HeroMarqueeItem.objects.all(),
        "featured_work_section": FeaturedWorkSection.objects.first(),
        "featured_works": Portfolio.objects.filter(featured=True).order_by("order"),
        "services_section": ServicesSection.objects.first(),
        "services": [],  # TODO: مدل Service هنوز پیاده‌سازی نشده
        "clients": ClientMarqueeItem.objects.all(),
        "manifesto": ManifestoSection.objects.first(),
        "cta": CTASection.objects.first(),
    }

    return render(request, "home/index.html", context)
