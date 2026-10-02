from django.shortcuts import render, get_object_or_404
from .context_utils import crumbs
from .models import (
    AboutPageHero,
    AboutStory,
    TeamMember,
    AboutValue,
    AboutStat,
    AboutPre,
    AboutMission,
    AboutProcessStep,
    AboutFaq,
    Proposal,
)


def about(request):
    context = {
        "crumbs": crumbs(("خانه", "home:home"), ("درباره ما", None)),
        "hero": AboutPageHero.objects.first(),
        "story": AboutStory.objects.first(),
        "team": TeamMember.objects.all(),
        "values": AboutValue.objects.all(),
        "stats": AboutStat.objects.all(),
        "pre": AboutPre.objects.first(),
        "mission": AboutMission.objects.first(),
        "process_steps": AboutProcessStep.objects.all(),
        "faqs": AboutFaq.objects.all(),
    }
    return render(request, "core/about.html", context)


def proposal(request, slug):
    proposal = get_object_or_404(Proposal, slug=slug)
    context = {
        "proposal": proposal,
        "stats": proposal.stats.all(),
        "problems": proposal.problems.all(),
        "essential_services": proposal.services.filter(service_type="essential"),
        "optional_services": proposal.services.filter(service_type="optional"),
    }
    return render(request, "core/proposal.html", context)
