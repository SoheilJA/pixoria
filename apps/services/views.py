from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from apps.blog.models import Article
from apps.core.context_utils import crumbs
from apps.home.models import FaqItem, FaqSection
from apps.portfolio.models import Portfolio

from .models import Service, ServicesHowSection, ServicesPageSection


def services_list(request):
    """صفحهٔ فهرستِ خدمات (v2 — T69).

    هر بخش با ``{% if %}``` در قالب محافظت می‌شود، تا صفحه با دیتابیسِ خالی
    (هیچ خدمتی، هیچ بخشِ FAQ) هم بدون خطا رندر شود.
    """
    faq_section = FaqSection.objects.first()
    how_section = ServicesHowSection.objects.first()
    return render(
        request,
        "services/list.html",
        {
            "crumbs": crumbs(("خانه", "home:home"), ("خدمات", None)),
            "page_section": ServicesPageSection.objects.first(),
            "services": list(Service.objects.all()),
            # بخشِ «چطور انتخاب کنیم» — تک‌سکشن + گام‌های مرتب‌شده (T69).
            "how_section": how_section,
            "steps": how_section.steps.all() if how_section else [],
            # FAQِ عمومیِ سایت (همان سوالاتِ صفحهٔ اصلی) — فقط وقتی وجود دارد.
            "faq_section": faq_section,
            "faq_items": (
                FaqItem.objects.filter(is_active=True) if faq_section else []
            ),
        },
    )


def services_detail(request, slug):
    """صفحهٔ اختصاصیِ خدمت (v2).

    تمامِ فرزندانِ خدمت در context فرستاده می‌شوند تا قالب هر کدام را با
    ``{% if %}`` محافظت کند؛ این‌طور صفحه با دیتابیسِ خالی (خدمتِ بدون هیچ
    فرزندی) هم بدون خطا رندر می‌شود.
    """

    service = get_object_or_404(Service, slug=slug)
    sections = list(service.sections.filter(is_active=True))

    context = {
        "crumbs": crumbs(
            ("خانه", "home:home"),
            ("خدمات", "services:list"),
            (service.title, None),
        ),
        "service": service,
        # مرور کلی = اولین بخشِ فعال (چیدمانِ تمام‌عرض در محتوای seeded)؛
        # بقیهٔ بخش‌ها به‌عنوانِ محتوای بلند در T64 رندر می‌شوند.
        "overview": sections[0] if sections else None,
        "sections": sections[1:],
        "deliverables": service.deliverables.all(),
        "tools": service.tools.all(),
        "use_cases": service.use_cases.all(),
        "stats": service.stats.all(),
        "why_us": service.why_us.all(),
        "processes": service.processes.all(),
        "plans": service.plans.filter(is_active=True).prefetch_related("features"),
        "custom_items": service.custom_items.all(),
        "faqs": service.faqs.all(),
        "related_services": list(service.related_services.all()),
        # هدرِ کاروسلِ نمونه‌کارها فقط وقتی کارتی هست چاپ می‌شود؛ همین کوئریِ
        # کامپوننتِ projects_carousel (FK + فیلدِ متنیِ fallback) از T61.
        "has_projects": Portfolio.objects.filter(
            Q(service=service) | Q(service_type=service.title)
        ).exists(),
        # همان قاعده برای کاروسلِ مقالات (M2Mِ related_services از T61).
        "has_articles": Article.objects.filter(
            status="published",
            published_at__lte=timezone.now(),
            related_services=service,
        ).exists(),
    }
    return render(request, "services/detail.html", context)
