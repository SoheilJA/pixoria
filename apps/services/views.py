from django.shortcuts import render, get_object_or_404
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
    service = get_object_or_404(Service, slug=slug)
    context = {
        "crumbs": crumbs(
            ("خانه", "home:home"),
            ("خدمات", "services:list"),
            (service.title, None),
        ),
        "service": service,
        "stats": service.stats.all(),
        "why_us": service.why_us.all(),
        "deliverables": service.deliverables.all(),
        "processes": service.processes.all(),
        "plans": service.plans.prefetch_related("features").all(),
        "custom_items": service.custom_items.all(),
        "faqs": service.faqs.all(),
        "other_services": Service.objects.exclude(slug=slug)[:4],
    }
    return render(request, "services/detail.html", context)
