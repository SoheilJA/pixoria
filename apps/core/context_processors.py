from .models import SiteSettings, SocialLink
from apps.home.models import CTASection
from apps.services.models import Service


def site_context(request):
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None

    socials = SocialLink.objects.all()
    cta = CTASection.objects.first()
    services_footer=Service.objects.all()[:5]

    return {
        "settings": settings,
        "socials": socials,
        "cta": cta,
        "services_footer": services_footer,
    }
