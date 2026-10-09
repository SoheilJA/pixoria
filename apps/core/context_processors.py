from .brand_utils import resolve_brand
from .models import SiteSettings, SocialLink, AboutStat, FooterLinkGroup
from apps.home.models import CTASection, HeaderSettings, NavItem
from apps.services.models import Service


def site_context(request):
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None

    socials = SocialLink.objects.all()
    cta = CTASection.objects.first()
    services_footer = Service.objects.all()[:5]
    stats = AboutStat.objects.all()
    footer_groups = list(
        FooterLinkGroup.objects.filter(is_active=True).prefetch_related("links")
    )
    footer_groups = [
        group for group in footer_groups if group.links.filter(is_active=True).exists()
    ]

    return {
        "settings": settings,
        # برند: لوگوی آپلودشده یا گزینهٔ پیش‌فرض + فاوآیکون و آیکون‌های PWA (T58).
        "brand": resolve_brand(settings, request=request),
        "socials": socials,
        "cta": cta,
        "services_footer": services_footer,
        "stats": stats,
        "header_settings": HeaderSettings.objects.first(),
        "nav_items": NavItem.objects.filter(is_active=True),
        "footer_groups": footer_groups,
    }
