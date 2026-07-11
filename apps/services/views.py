from django.shortcuts import render, get_object_or_404
from .models import Service, ServicesPageSection


def services_list(request):
    context = {
        "page_section": ServicesPageSection.objects.first(),
        "services": Service.objects.all(),
    }
    return render(request, "services/list.html", context)


def services_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    context = {
        "service": service,
        "stats": service.stats.all(),
        "why_us": service.why_us.all(),
        "deliverables": service.deliverables.all(),
        "processes": service.processes.all(),
        "plans": service.plans.all(),
        "custom_items": service.custom_items.all(),
        "faqs": service.faqs.all(),
        "testimonials": service.testimonials.all(),
        "other_services": Service.objects.exclude(slug=slug)[:4],
    }
    return render(request, "services/detail.html", context)
