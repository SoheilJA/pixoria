from .models import SiteSettings, SocialLink


def site_context(request):
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None

    socials = SocialLink.objects.all()

    return {"settings": settings, "socials": socials}
