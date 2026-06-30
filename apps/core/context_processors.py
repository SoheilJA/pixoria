from .models import SiteSettings, SocialLink
from apps.home.models import CTASection


def site_context(request):
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None

    socials = SocialLink.objects.all()
    cta = CTASection.objects.first()

    return {"settings": settings, "socials": socials, "cta": cta}
