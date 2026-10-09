from django.shortcuts import get_object_or_404, render

from apps.core.context_utils import crumbs

from .models import Service, ServicesPageSection


def services_list(request):
    context = {
        "crumbs": crumbs(("خانه", "home:home"), ("خدمات", None)),
        "page_section": ServicesPageSection.objects.first(),
        "services": list(Service.objects.all()),
    }
    return render(request, "services/list.html", context)


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
    }
    return render(request, "services/detail.html", context)
