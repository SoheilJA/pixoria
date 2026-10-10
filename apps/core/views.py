import math

from django.shortcuts import render, get_object_or_404
from .brand_utils import resolve_brand
from .context_utils import crumbs
from .models import (
    SiteSettings,
    AboutPageHero,
    AboutStory,
    AboutJourneySection,
    AboutJourneyStep,
    AboutClientsSection,
    AboutStat,
    Proposal,
)
from apps.home.models import ClientMarqueeItem
from apps.services.models import Service

# موقعیتِ پنج ایستگاهِ مسیر در طرح v2 (مختصات viewBox 1000×340). وقتی تعداد
# ایستگاه‌ها دقیقاً پنج باشد همین نقاط دقیق استفاده می‌شوند.
JOURNEY_DESIGN_POSITIONS = [
    (40, 250),
    (247, 111),
    (500, 160),
    (653, 175),
    (960, 70),
]
JOURNEY_VIEWBOX = (1000, 340)


def journey_points(count):
    """مختصات ایستگاه‌های مسیر — روی یک قوس نرم توزیع می‌شوند.

    طرح اصلی پنج ایستگاه با موقعیت‌های ثابت دارد؛ اگر مدیر تعداد را تغییر داد،
    ایستگاه‌ها به‌صورت یکنواخت روی viewBox پخش و روی یک قوس سینوسی نرم نشان
    داده می‌شوند تا مسیر و گره‌ها همیشه هم‌خوان بمانند."""
    if count == len(JOURNEY_DESIGN_POSITIONS):
        return list(JOURNEY_DESIGN_POSITIONS)
    if count < 2:
        return [(500, 170)] * max(count, 0)
    w, h = JOURNEY_VIEWBOX
    return [
        (
            round(40 + (w - 80) * i / (count - 1)),
            round(h * 0.62 - h * 0.32 * math.sin(math.pi * i / (count - 1))),
        )
        for i in range(count)
    ]


def journey_path(points):
    """مسیرِ نرم (quadratic) از روی ایستگاه‌ها — برای SVGیِ نسخهٔ دسکتاپ."""
    if len(points) < 2:
        return ""
    x0, y0 = points[0]
    parts = [f"M{x0} {y0}"]
    for i in range(1, len(points) - 1):
        px, py = points[i]
        nx, ny = points[i + 1]
        parts.append(f"Q{px} {py} {(px + nx) / 2:.1f} {(py + ny) / 2:.1f}")
    lx, ly = points[-1]
    parts.append(f"L{lx} {ly}")
    return " ".join(parts)


def about(request):
    # ایستگاه‌های مسیر به همراه موقعیتِ روی نقشهٔ SVG annotate می‌شوند تا
    # قالب فقط داده را رندر کند و محاسبه در سمت سرور بماند.
    steps = list(AboutJourneyStep.objects.all())
    points = journey_points(len(steps))
    for index, (step, point) in enumerate(zip(steps, points)):
        step.point_x, step.point_y = point
        # برچستِ پررنگِ هر گره: سالِ ایستگاه‌های اول و آخر، عنوان بقیه. برچسب
        # کوچک هم مکمل آن است (عنوان یا زیرعنوان).
        step.label_below = index % 2 == 0
        step.label_bold = step.year or step.title
        step.label_small = step.title if step.year else step.subtitle

    context = {
        "crumbs": crumbs(("خانه", "home:home"), ("درباره ما", None)),
        "hero": AboutPageHero.objects.first(),
        "story": AboutStory.objects.first(),
        "journey": AboutJourneySection.objects.first(),
        "journey_steps": steps,
        "journey_path": journey_path(points),
        "clients_section": AboutClientsSection.objects.first(),
        # دیوار برندها همان برندهای بخش «اعتماد» صفحه اصلی است — یک منبع داده.
        "clients": ClientMarqueeItem.objects.all(),
        # سیاره‌های سامانهٔ خورشیدیِ هیرو از خدمات دیتابیس می‌آیند (تا ۶ مورد).
        "services": Service.objects.all()[:6],
        "stats": AboutStat.objects.all(),
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


def manifest(request):
    """site.webmanifest — آیکون‌های PWA از برندِ انتخاب‌شده می‌آیند (T58).

    مانیفست باید از فاوآیکونِ گزینهٔ منتخب (یا فایل آپلودشده) بخواند، پس
    نمی‌تواند استاتیک باشد. مقادیرها با فیلتر json دورریخته می‌شوند تا یک
    کوتیشن داخل نام سایت کل JSON را نشکنند.
    """
    try:
        site_settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        site_settings = None
    brand = resolve_brand(site_settings, request=request)
    return render(
        request,
        "manifest.webmanifest",
        {"brand": brand},
        content_type="application/manifest+json",
    )
