from django.shortcuts import render
from django.utils import timezone
from .models import (
    HeroSection,
    HeroMarqueeItem,
    FeaturedWorkSection,
    ServicesSection,
    ClientMarqueeItem,
    ManifestoSection,
    CTASection,
    LatestArticlesSection,
)
from apps.portfolio.models import Portfolio
from apps.services.models import Service, ServiceTestimonial
from apps.blog.models import Article


def home(request):
    featured_services = list(Service.objects.filter(featured=True))
    context = {
        "hero": HeroSection.objects.first(),
        "hero_marquee": HeroMarqueeItem.objects.all(),
        "featured_work_section": FeaturedWorkSection.objects.first(),
        "featured_works": Portfolio.objects.filter(featured=True)[:3],
        "services_section": ServicesSection.objects.first(),
        "services": featured_services,
        "services_with_delay": [
            {"service": service, "delay": (index % 5) * 100}
            for index, service in enumerate(featured_services)
        ],
        "clients": ClientMarqueeItem.objects.all(),
        "manifesto": ManifestoSection.objects.first(),
        "cta": CTASection.objects.first(),
        "testimonials": ServiceTestimonial.objects.filter(show_on_home=True),
        "latest_articles_section": LatestArticlesSection.objects.first(),
        "latest_articles": Article.objects.filter(
            status="published", published_at__lte=timezone.now()
        )
        .select_related("category")
        .order_by("-published_at")[:8],
    }
    return render(request, "home/index.html", context)
