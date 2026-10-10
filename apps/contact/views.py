"""نمای صفحهٔ «تماس با ما» و پردازش فرم آن.

GET صفحه را رندر می‌کند و POST (فقط از طریق HTMX) فرم را اعتبارسنجی کرده و
در `ContactSubmission` ذخیره می‌کند. در پاسخ، همان فرم به‌همراه خطاها یا حالت
موفقیت برمی‌گردد — هر دو با ۲۰۰ تا htmx بدون تنظیمات اضافه swap کند."""

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from apps.core.context_utils import crumbs
from apps.core.models import SiteSettings, SocialLink
from apps.services.models import Service

from .forms import ContactSubmissionForm
from .models import (
    ContactPageSection,
    ContactFormSection,
    ContactFormPoint,
    ContactMapSection,
    ContactFaqSection,
    ContactFaq,
    ContactSubmission,
    SubjectChoice,
)

# محدودیت نرخ — مثل فرم تماس سریعِ صفحه اصلی.
RATE_LIMIT = 5  # حداکثر ارسال در هر پنجره
RATE_WINDOW = 3600  # ثانیه

# موضوعِ پیش‌پر شدهٔ فرم — لینک‌های «ثبت سفارش» پلن‌ها این کلیدواژه‌ها را
# می‌فرستند (در SubjectChoice هستند تا clean_subject آن‌ها را بپذیرد).
SERVICE_SUBJECT = "مشاورهٔ خدمات"
ORDER_SUBJECT = "درخواست سفارش پروژه"


def _rate_key(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "")
    return f"pixoria:contact:{ip}"


def _prefill(request):
    """موضوع و متنِ فرمِ تماس را از پارامترهای ``?service=<slug>&plan=<type>``
    پر می‌کند (لینکِ دکمهٔ پلن‌های صفحهٔ خدمت).

    فقط مقادیرِ معتبر پیش‌پر می‌شوند: خدمت باید وجود داشته باشد و نوعِ پلن
    باید یکی از پلن‌های همان خدمت باشد. یک لینکِ خراب هرگز فرم را نمی‌شکند —
    مثلِ رفتارِ بدونِ پارامتر برمی‌گردد. موضوع هم فقط وقتی تنظیم می‌شود که
    در SubjectChoice وجود داشته باشد (admin ممکن است آن را حذف کرده باشد).

    خروجی: (initial, note) — initial برای ModelForm و note یک خطِ اطلاع‌رسانی
    بالایِ فرم.
    """
    if request is None:
        return {}, ""

    service_slug = request.GET.get("service", "").strip()
    plan_type = request.GET.get("plan", "").strip()
    if not service_slug and not plan_type:
        return {}, ""

    service = None
    if service_slug:
        service = Service.objects.filter(slug=service_slug).first()
        # slug نادرست → لینک خراب است؛ هیچ پیش‌پر‌ای نکنیم.
        if service is None:
            return {}, ""

    plan_name = ""
    if plan_type:
        if service is None:
            # پلن بدونِ خدمت: فقط موضوعِ «سفارش پروژه» کافی است.
            pass
        else:
            plan = service.plans.filter(plan_type=plan_type).first()
            # نوعِ پلنِ نادرست برای این خدمت → باز هم لینکِ خراب.
            if plan is None:
                return {}, ""
            plan_name = plan.name

    # موضوع: سفارشِ پروژه وقتی پلن داده شده، وگرنه مشاورهٔ خدمات.
    subject = ORDER_SUBJECT if plan_type else SERVICE_SUBJECT
    if not SubjectChoice.objects.filter(label=subject).exists():
        subject = ""

    parts = []
    if service is not None:
        parts.append(f"خدمتِ «{service.title}»")
    if plan_name:
        parts.append(f"پلنِ «{plan_name}»")

    initial = {}
    if subject:
        initial["subject"] = subject
    if parts:
        initial["message"] = "درخواستِ مشاوره برای " + " — ".join(parts) + "."

    note = ""
    if parts:
        note = " · ".join(parts)

    return initial, note


def _page_context(request=None):
    initial, note = _prefill(request)
    return {
        "crumbs": crumbs(("خانه", "home:home"), ("تماس با ما", None)),
        "page_section": ContactPageSection.objects.first(),
        "form_section": ContactFormSection.objects.first(),
        "form_points": ContactFormPoint.objects.filter(is_active=True),
        "map_section": ContactMapSection.objects.first(),
        "faq_section": ContactFaqSection.objects.first(),
        "faq_items": ContactFaq.objects.all(),
        "socials": SocialLink.objects.all(),
        "form": ContactSubmissionForm(initial=initial),
        "prefill_note": note,
    }


@never_cache
@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == "POST":
        return _handle_submit(request)
    return render(request, "contact/contact.html", _page_context(request))


def _handle_submit(request):
    form = ContactSubmissionForm(request.POST)

    # هانی‌پات: فیلد مخفی برای ربات‌ها. در ظاهر موفق برمی‌گردانیم تا
    # فرستنده متوجه نخشنودن درخواستش نشود.
    if request.POST.get("company_website", ""):
        return render(
            request, "contact/_contact_success.html", _page_context()
        )

    key = _rate_key(request)
    if cache.get(key, 0) >= RATE_LIMIT:
        context = _page_context()
        context["rate_limited"] = True
        context["form"] = form
        return render(request, "contact/_contact_form.html", context)

    if not form.is_valid():
        cache.set(key, cache.get(key, 0) + 1, RATE_WINDOW)
        context = _page_context()
        context["form"] = form
        return render(request, "contact/_contact_form.html", context)

    submission = form.save()
    cache.set(key, cache.get(key, 0) + 1, RATE_WINDOW)

    # اعلان ایمیلی فقط اگر تنظیمات ایمیل از قبل موجود باشد — و هرگز نباید
    # شکستِ سرور ایمیل، ثبت پیام کاربر را خراب کند.
    _maybe_notify(submission)

    return render(request, "contact/_contact_success.html", _page_context())


def _maybe_notify(submission):
    """اگر EMAIL_HOST تنظیم شده باشد، رونوشت پیام را به ایمیل سایت می‌فرستد."""
    if not getattr(settings, "EMAIL_HOST", None):
        return
    site = SiteSettings.objects.first()
    if not site or not site.email:
        return
    try:
        send_mail(
            subject=f"پیام جدید از صفحهٔ تماس: {submission.subject or 'بدون موضوع'}",
            message=(
                f"نام: {submission.name}\n"
                f"ایمیل: {submission.email}\n"
                f"تلفن: {submission.phone or '—'}\n"
                f"موضوع: {submission.subject or '—'}\n\n"
                f"{submission.message}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL or site.email,
            recipient_list=[site.email],
            fail_silently=True,
        )
    except Exception:  # noqa: BLE001 — ایمیل هرگز نباید فرم را بشکند
        pass
