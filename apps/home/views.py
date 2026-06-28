from django.shortcuts import render
from .models import *


def home(request):
    context = {
        "hero": HeroSection.objects.first(),
        "hero_marquee": HeroMarqueeItem.objects.all(),
        "featured_work_section": FeaturedWorkSection.objects.first(),
        "services_section": ServicesSection.objects.first(),
        'services':[],
        "clients": ClientMarqueeItem.objects.all(),
        "manifesto": ManifestoSection.objects.first(),
        "cta": CTASection.objects.first(),
    }

    return render(request, "home/index.html", context)
