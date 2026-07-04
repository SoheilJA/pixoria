from django.shortcuts import render
from .models import (
    AboutPageHero,
    AboutStory,
    TeamMember,
    AboutValue,
    AboutStat,
    AboutPre,
)


def about(request):
    context = {
        "hero": AboutPageHero.objects.first(),
        "story": AboutStory.objects.first(),
        "team": TeamMember.objects.all(),
        "values": AboutValue.objects.all(),
        "stats": AboutStat.objects.all(),
        "pre": AboutPre.objects.first(),
    }

    return render(request, "core/about.html", context)
