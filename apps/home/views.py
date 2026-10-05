from django.core.cache import cache
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

import json

from .models import (
    ContactSection,
    FaqItem,
    FaqSection,
    FeaturedWorkSection,
    HeaderSettings,
    HeroMarqueeItem,
    HeroSection,
    HeroStat,
    HomeAboutSection,
    HomeAboutStat,
    HomeLead,
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
    ClientMarqueeItem,
)
from apps.portfolio.models import Category, Portfolio
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
        "hero_stats": HeroStat.objects.filter(is_active=True) if "hero" in keys else [],
        "services_section": ServicesSection.objects.first() if "services" in keys else None,
        "services": featured_services,
        "services_with_delay": [
            {"service": service, "delay": (index % 5) * 100}
            for index, service in enumerate(featured_services)
        ],
        "testimonials": (
            ServiceTestimonial.objects.filter(show_on_home=True) if "testimonials" in keys else []
        ),
        "testimonials_section": TestimonialSection.objects.first() if "testimonials" in keys else None,
        "latest_articles": (
            Article.objects.filter(status="published", published_at__lte=timezone.now())
            .select_related("category")
            .order_by("-published_at")[:8]
            if "blog" in keys
            else []
        ),
        # ── بخش‌های جدید ──
        "about_section": HomeAboutSection.objects.first() if "about" in keys else None,
        "about_stats": HomeAboutStat.objects.filter(is_active=True) if "about" in keys else [],
        "trusted_section": TrustedSection.objects.first() if "trusted" in keys else None,
        "clients": ClientMarqueeItem.objects.all() if "trusted" in keys else [],
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
        "faq_section": FaqSection.objects.first() if "faq" in keys else None,
        "faq_items": FaqItem.objects.filter(is_active=True) if "faq" in keys else [],
        "contact_section": ContactSection.objects.first() if "contact" in keys else None,
        "contact_services": Service.objects.filter(featured=True) if "contact" in keys else [],
    }

    # ── نمونه‌کارهای صفحه اصلی: پروژه‌های منتخب، همراه با دسته‌بندی برای فیلتر ──
    if "portfolio" in keys:
        context["portfolio_items"] = list(
            Portfolio.objects.filter(featured=True).prefetch_related("categories")
        )
        # فقط دسته‌بندی‌هایی دکمهٔ فیلتر می‌گیرند که روی این پروژه‌ها فعال باشند.
        context["portfolio_categories"] = list(
            Category.objects.filter(portfolio__featured=True).distinct().order_by("order", "id")
        )

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


# ══════════════════════════════════════════════════════════════════
# فرم تماس سریع — HTMX POST + هانی‌پات + محدودیت نرخ
# ══════════════════════════════════════════════════════════════════
LEAD_RATE_LIMIT = 5 # حداکثر ارسال در هر پنجره
LEAD_RATE_WINDOW = 3600 # ثانیه


def _lead_rate_key(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "")
    return f"pixoria:home-lead:{ip}"


def _lead_context(contact_section=None, **extra):
    context = {
        "contact_section": contact_section or ContactSection.objects.first(),
        "contact_services": list(Service.objects.filter(featured=True)),
    }
    context.update(extra)
    return context


@require_POST
@never_cache
def lead(request):
    """ثبت درخواست تماس سریع. فقط HTMX فراخوانی می‌کند و در پاس، حالت
    موفقیت یا همان فرم به‌همراه خطاها را برمی‌گرداند (هر دو با ۲۰۰ تا
    htmx بدون نیاز به تنظیمات اضافه swap کند)."""

    # هانی‌پات: فیلد مخفی برای ربات‌ها. در ظاهر موفق برمی‌گردانیم تا
    # فرستنده متوجه نخشنودن درخواستش نشود.
    if request.POST.get("company_website", ""):
        return render(
            request, "home/sections/_lead_success.html", _lead_context()
        )

    key = _lead_rate_key(request)
    if cache.get(key, 0) >= LEAD_RATE_LIMIT:
        return render(
            request,
            "home/sections/_lead_form.html",
            _lead_context(rate_limited=True),
        )

    name = request.POST.get("name", "").strip()
    phone = request.POST.get("phone", "").strip()
    message = request.POST.get("message", "").strip()
    service_id = request.POST.get("service", "").strip()

    errors = {}
    if len(name) < 3:
        errors["name"] = "نام و نام خانوادگی را کامل وارد کنید."
    if len(phone) < 7 or len(phone) > 20:
        errors["phone"] = "یک شماره تماس معتبر وارد کنید."
    if len(message) < 10:
        errors["message"] = "پیام را کمی طولانی‌تر بنویسید (حداقل ۱۰ نویسه)."

    if errors:
        cache.set(key, cache.get(key, 0) + 1, LEAD_RATE_WINDOW)
        return render(
            request,
            "home/sections/_lead_form.html",
            _lead_context(
                errors=errors,
                form_data={"name": name, "phone": phone, "message": message, "service": service_id},
            ),
        )

    service = None
    if service_id:
        try:
            service = Service.objects.get(pk=service_id)
        except (Service.DoesNotExist, ValueError):
            service = None

    HomeLead.objects.create(name=name, phone=phone, service=service, message=message)
    cache.set(key, cache.get(key, 0) + 1, LEAD_RATE_WINDOW)

    return render(
        request, "home/sections/_lead_success.html", _lead_context()
    )
