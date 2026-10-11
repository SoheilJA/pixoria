from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe

import json

from .models import (
    FaqItem,
    FaqSection,
    FeaturedWorkSection,
    HeaderSettings,
    HeroSection,
    HeroStat,
    HomeAboutSection,
    HomeAboutStat,
    HomeSection,
    LatestArticlesSection,
    ProcessSection,
    ProcessStep,
    ServicesSection,
    StatItem,
    StatsSection,
    TechSection,
    TechSkill,
    TestimonialSection,
    TrustedSection,
    WhyFeature,
    WhySection,
)
from apps.portfolio.models import Category, Portfolio
from apps.services.models import Service


def home(request):
    """صفحه اصلی — بخش‌ها به ترتیب و وضعیت تعریف‌شده در پنل ادمین رندر می‌شوند.

    هر بخش فقط در صورت فعال‌بودن کوئری می‌شود تا صفحه سبک بماند."""
    sections = list(HomeSection.objects.filter(is_active=True).order_by("order", "id"))
    keys = {section.key for section in sections}

    featured_services = list(Service.objects.filter(featured=True)) if "services" in keys else []

    context = {
        "sections": sections,
        "blog_url": reverse("blog:list"),
        # ── بخش‌های موجود (جریان داده دست‌نخورده) ──
        "hero": HeroSection.objects.first() if "hero" in keys else None,
        "hero_stats": HeroStat.objects.filter(is_active=True) if "hero" in keys else [],
        "services_section": ServicesSection.objects.first() if "services" in keys else None,
        "services": featured_services,
        "testimonials_section": TestimonialSection.objects.first() if "testimonials" in keys else None,
        # ── بخش‌های جدید ──
        "about_section": HomeAboutSection.objects.first() if "about" in keys else None,
        "about_stats": HomeAboutStat.objects.filter(is_active=True) if "about" in keys else [],
        "trusted_section": TrustedSection.objects.first() if "trusted" in keys else None,
        # برندهای مارکوییِ «اعتماد» از نام مشتریِ نمونه‌کارها خوانده می‌شوند —
        # هر نمونه‌کاری که در ادمین بارگذاری می‌شود، برندش اینجا ظاهر می‌شود.
        "clients": (
            Portfolio.objects.exclude(client_name="")
            .order_by("order", "id")
            .values_list("client_name", flat=True)
            .distinct()
            if "trusted" in keys
            else []
        ),
        "portfolio_section": FeaturedWorkSection.objects.first() if "portfolio" in keys else None,
        "portfolio_items": [],
        "blog_section": LatestArticlesSection.objects.first() if "blog" in keys else None,
        "stats_section": StatsSection.objects.first() if "stats" in keys else None,
        "stats": StatItem.objects.filter(is_active=True) if "stats" in keys else [],
        "process_section": ProcessSection.objects.first() if "process" in keys else None,
        "process_steps": ProcessStep.objects.filter(is_active=True) if "process" in keys else [],
        "why_section": WhySection.objects.first() if "why" in keys else None,
        "why_features": WhyFeature.objects.filter(is_active=True) if "why" in keys else [],
        "tech_section": TechSection.objects.first() if "tech" in keys else None,
        "tech_skills": TechSkill.objects.filter(is_active=True) if "tech" in keys else [],
        "tech_row1": [],
        "tech_row2": [],
        "faq_section": FaqSection.objects.first() if "faq" in keys else None,
        "faq_items": FaqItem.objects.filter(is_active=True) if "faq" in keys else [],
    }

    # ── نمونه‌کارهای صفحه اصلی: پروژه‌های منتخب، همراه با دسته‌بندی برای فیلتر ──
    if "portfolio" in keys:
        pf_items = list(
            Portfolio.objects.filter(featured=True)
            .order_by("order", "id")
            .prefetch_related("categories")[:9]
        )
        # گرید سه‌ستونه است؛ تعداد باید مضربی از ۳ باشد تا ردیف آخر یتیم نماند.
        # وقتی پروژه‌ها ۳ تا یا کمترند همه‌شان را نشان می‌دهیم (پنهان کردن محتوا
        # از زیباییِ گرید مهم‌تر است).
        if len(pf_items) > 3:
            pf_items = pf_items[: len(pf_items) - len(pf_items) % 3]
        context["portfolio_items"] = pf_items
        # فقط دسته‌بندی‌هایی دکمهٔ فیلتر می‌گیرند که روی این پروژه‌ها فعال باشند.
        context["portfolio_categories"] = list(
            Category.objects.filter(portfolio__featured=True).distinct().order_by("order", "id")
        )

    # ─ـ مهارت‌ها در دو ردیفِ مارکویی تقسیم می‌شوند ──
    if "tech" in keys:
        skills = list(context["tech_skills"])
        midpoint = (len(skills) + 1) // 2
        context["tech_row1"] = skills[:midpoint]
        context["tech_row2"] = skills[midpoint:]

    # ── دادهٔ ساختاریافتهٔ FAQ برای موتورهای جستجو (schema.org/FAQPage) ──
    if "faq" in keys:
        faq_items = context["faq_items"]
        context["faq_json"] = faq_structured_data(faq_items)

    return render(request, "home/index.html", context)


def faq_structured_data(faq_items):
    """FAQPage JSON-LD. `</` is escaped so a scripted string can never close
    the tag early, and mark_safe keeps the JSON inside the ld+json script."""

    payload = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item.question,
                "acceptedAnswer": {"@type": "Answer", "text": item.answer},
            }
            for item in faq_items
        ],
    }
    return mark_safe(json.dumps(payload, ensure_ascii=False).replace("</", "<\\/"))
