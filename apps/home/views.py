from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .models import (
    ContactSection,
    FaqItem,
    FaqSection,
    FeaturedWorkSection,
    HeaderSettings,
    HeroMarqueeItem,
    HeroSection,
    HomeSection,
    LatestArticlesSection,
    ManifestoSection,
    Package,
    PackagesSection,
    ProcessSection,
    ProcessStep,
    ServicesSection,
    StatItem,
    StatsSection,
    TechSection,
    TechSkill,
    WhyFeature,
    WhySection,
    ClientMarqueeItem,
)
from apps.portfolio.models import Portfolio
from apps.services.models import Service, ServiceTestimonial
from apps.blog.models import Article


def home(request):
    """صفحه اصلی — بخش‌ها به ترتیب و وضعیت تعریف‌شده در پنل ادمین رندر می‌شوند.

    هر بخش فقط در صورت فعال‌بودن کوئری می‌شود تا صفحه سبک بماند."""
    sections = list(HomeSection.objects.filter(is_active=True).order_by("order", "id"))
    keys = {section.key for section in sections}

    featured_services = list(Service.objects.filter(featured=True)) if "services" in keys else []

    context = {
        "sections": sections,
        "contact_url": reverse("contact:contact"),
        "portfolio_url": reverse("portfolio:list"),
        "blog_url": reverse("blog:list"),
        # ── بخش‌های موجود (جریان داده دست‌نخورده) ──
        "hero": HeroSection.objects.first() if "hero" in keys else None,
        "hero_marquee": HeroMarqueeItem.objects.all(),
        "featured_work_section": FeaturedWorkSection.objects.first() if "works" in keys else None,
        "featured_works": Portfolio.objects.filter(featured=True)[:3] if "works" in keys else [],
        "services_section": ServicesSection.objects.first() if "services" in keys else None,
        "services": featured_services,
        "services_with_delay": [
            {"service": service, "delay": (index % 5) * 100}
            for index, service in enumerate(featured_services)
        ],
        "clients": ClientMarqueeItem.objects.all() if "clients" in keys else [],
        "manifesto": ManifestoSection.objects.first() if "manifesto" in keys else None,
        "testimonials": (
            ServiceTestimonial.objects.filter(show_on_home=True) if "testimonials" in keys else []
        ),
        "latest_articles_section": LatestArticlesSection.objects.first() if "articles" in keys else None,
        "latest_articles": (
            Article.objects.filter(status="published", published_at__lte=timezone.now())
            .select_related("category")
            .order_by("-published_at")[:8]
            if "articles" in keys
            else []
        ),
        # ── بخش‌های جدید ──
        "stats_section": StatsSection.objects.first() if "stats" in keys else None,
        "stats": StatItem.objects.filter(is_active=True) if "stats" in keys else [],
        "process_section": ProcessSection.objects.first() if "process" in keys else None,
        "process_steps": ProcessStep.objects.filter(is_active=True) if "process" in keys else [],
        "why_section": WhySection.objects.first() if "why" in keys else None,
        "why_features": WhyFeature.objects.filter(is_active=True) if "why" in keys else [],
        "tech_section": TechSection.objects.first() if "tech" in keys else None,
        "tech_skills": TechSkill.objects.filter(is_active=True) if "tech" in keys else [],
        "packages_section": PackagesSection.objects.first() if "packages" in keys else None,
        "packages": (
            Package.objects.filter(is_active=True).prefetch_related("features")
            if "packages" in keys
            else []
        ),
        "faq_section": FaqSection.objects.first() if "faq" in keys else None,
        "faq_items": FaqItem.objects.filter(is_active=True) if "faq" in keys else [],
        "contact_section": ContactSection.objects.first() if "contact" in keys else None,
        "contact_services": Service.objects.filter(featured=True) if "contact" in keys else [],
    }
    return render(request, "home/index.html", context)
