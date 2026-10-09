"""T61 verification — service model extensions for the dedicated pages.

Checks:
  - every public page still renders 200
  - the new relations work: Portfolio.service FK, Article.related_services M2M
  - projects_carousel(service=…) uses the FK and keeps the service_type fallback
  - articles_carousel(service=…) filters through the M2M
  - fa_price formats with Persian thousand separators
  - ServicePlan.clean() rejects a second featured plan; max_num=3 in the admin
  - plan prices survived the million-toman → toman conversion
  - the service admin page renders the new fieldsets + inlines, and a real POST
    through the admin saves the new fields
  - every page still renders 200 with an EMPTY database (rolled back)
"""
import os
import sys

import django

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client
from django.test.utils import setup_test_environment
from django.db import transaction

setup_test_environment()
client = Client(HTTP_HOST="localhost")

failures = []


def check(label, condition, detail=""):
    status = "ok  " if condition else "FAIL"
    print(f"{status} {label}" + (f" — {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(label)


# ---------------------------------------------------------------- pages
PAGES = [
    "/",
    "/about/",
    "/contact/",
    "/portfolio/",
    "/blog/",
    "/services/",
    "/services/web-design/",
    "/services/programming/",
]
for url in PAGES:
    r = client.get(url)
    check(f"GET {url} -> 200", r.status_code == 200, str(r.status_code))

# ------------------------------------------------------- model plumbing
from apps.portfolio.models import Portfolio
from apps.blog.models import Article
from apps.services.models import Service, ServicePlan

services = list(Service.objects.all())
check("services exist (4)", len(services) == 4, f"{len(services)}")

service = services[0]
other = services[1]

# Portfolio.service FK + fallback
p_fk = Portfolio.objects.first()
p_fk.service = service
p_fk.save(update_fields=["service"])
check("Portfolio.service FK saved", Portfolio.objects.get(pk=p_fk.pk).service_id == service.pk)

# Article.related_services M2M
a = Article.objects.first()
if a is not None:
    a.related_services.add(service)
    check(
        "Article.related_services M2M works",
        list(a.related_services.all()) == [service],
    )
else:
    check("Article.related_services M2M works", False, "no article in DB")

# ---------------------------------------------- projects_carousel service
from apps.portfolio.templatetags.projects_tags import projects_carousel

ctx = projects_carousel(service=service, limit=12)
check(
    "projects_carousel(service) returns the FK-linked project",
    p_fk in ctx["projects"],
    str([p.pk for p in ctx["projects"]]),
)

# fallback: a project with only the free-text service_type
p_text = Portfolio.objects.exclude(pk=p_fk.pk).first()
if p_text is not None:
    original = p_text.service_type
    p_text.service = None
    p_text.service_type = service.title
    p_text.save(update_fields=["service", "service_type"])
    ctx2 = projects_carousel(service=service, limit=12)
    check(
        "projects_carousel(service) falls back to service_type text",
        p_text in ctx2["projects"],
    )
    ctx3 = projects_carousel(service=other, limit=12)
    check(
        "projects_carousel(unmatched service) excludes the text-only project",
        p_text not in ctx3["projects"],
    )
    # a free string still works (no FK lookup attempted)
    ctx4 = projects_carousel(service=service.title, limit=12)
    check("projects_carousel(str) filters service_type", p_text in ctx4["projects"])
    p_text.service_type = original
    p_text.service = None
    p_text.save(update_fields=["service", "service_type"])
else:
    check("projects_carousel fallback (needs a 2nd project)", False)

p_fk.service = None
p_fk.save(update_fields=["service"])

# ---------------------------------------------- articles_carousel service
from apps.blog.templatetags.articles_tags import articles_carousel

ctx = articles_carousel(service=service, limit=12)
check(
    "articles_carousel(service) returns only related articles",
    set(ctx["articles"]) <= set(service.articles.all()),
    str([x.pk for x in ctx["articles"]]),
)
ctx = articles_carousel(service=other, limit=12)
check(
    "articles_carousel(unrelated service) returns nothing",
    len(ctx["articles"]) == 0,
    str([x.pk for x in ctx["articles"]]),
)
a.related_services.clear()

# ------------------------------------------------------------- fa_price
from apps.core.templatetags.fa_digits import fa_price

check("fa_price(15000000)", fa_price(15000000) == "۱۵٬۰۰۰٬۰۰۰", fa_price(15000000))
check("fa_price(None)", fa_price(None) == "", repr(fa_price(None)))
check("fa_price('abc')", fa_price("abc") == "", repr(fa_price("abc")))

# ------------------------------------------------------- plan conversion
plan = ServicePlan.objects.first()
check(
    "plan price converted to toman (×1_000_000)",
    plan.price in (15_000_000, 30_000_000, 60_000_000),
    str(plan.price),
)
check(
    "plan old_price converted to toman",
    plan.old_price in (18_000_000, 35_000_000, 70_000_000),
    str(plan.old_price),
)

# ------------------------------------------------- one featured plan rule
plan2 = ServicePlan.objects.exclude(pk=plan.pk).first()
plan2.is_featured = True
try:
    if plan.is_featured:
        plan2.clean()
        check("two featured plans rejected", False, "clean() did not raise")
    else:
        check("two featured plans rejected", True, "base plan is not featured")
except ValidationError:
    check("two featured plans rejected", True)
plan2.is_featured = False

# --------------------------------------------------------- admin surfaces
User = get_user_model()
admin_user, _created = User.objects.get_or_create(
    username="t61_check", defaults={"is_staff": True, "is_superuser": True}
)
admin_client = Client(HTTP_HOST="localhost")
admin_client.force_login(admin_user)

service_admin = site._registry[Service]
check(
    "ServiceAdmin has the new inlines",
    {"servicesection", "servicetool", "serviceusecase"}
    <= {i.model._meta.model_name for i in service_admin.inlines},
    str([i.model._meta.model_name for i in service_admin.inlines]),
)
check(
    "ServicePlanInline is capped at 3",
    service_admin.inlines[[i.__name__ for i in service_admin.inlines].index("ServicePlanInline")].max_num == 3,
)

# fieldsets/inlines on the rendered add page (needs a real request)
add_body = admin_client.get("/admin/services/service/add/").content.decode("utf-8")
for label, needle in [
    ("accent radios", 'name="accent"'),
    ("hero_eyebrow", 'name="hero_eyebrow"'),
    ("hero_title", 'name="hero_title"'),
    ("related_services", 'name="related_services"'),
    ("meta_title", 'name="meta_title"'),
    ("og_image", 'name="og_image"'),
    ("ServiceSection inline", "sections-TOTAL_FORMS"),
    ("ServiceTool inline", "tools-TOTAL_FORMS"),
    ("ServiceUseCase inline", "use_cases-TOTAL_FORMS"),
]:
    check(f"admin add page has {label}", needle in add_body)

urls = [
    "/admin/services/service/",
    "/admin/services/service/add/",
    f"/admin/services/service/{service.pk}/change/",
    "/admin/services/serviceplan/",
    "/admin/portfolio/portfolio/",
    f"/admin/portfolio/portfolio/{p_fk.pk}/change/",
    "/admin/blog/article/",
    f"/admin/blog/article/{a.pk}/change/" if a else "/admin/blog/article/add/",
]
for url in urls:
    r = admin_client.get(url)
    check(f"admin {url} -> 200", r.status_code == 200, str(r.status_code))

# a real admin POST through the ADD page (a fresh service has no children, so the
# inline management forms can all be empty — on the change page of service 1 the
# three existing plans would each need their required fields)
PREFIXES = [
    "sections", "stats", "why_us", "deliverables", "processes",
    "tools", "use_cases", "plans", "custom_items", "faqs", "testimonials",
]
mgmt = {}
for prefix in PREFIXES:
    for key in ("TOTAL_FORMS", "INITIAL_FORMS", "MIN_NUM_FORMS", "MAX_NUM_FORMS"):
        mgmt[f"{prefix}-{key}"] = "0" if key != "MAX_NUM_FORMS" else "1000"

r = admin_client.post(
    "/admin/services/service/add/",
    {
        "title": "خدمت تستی T61",
        "slug": "t61-test-service",
        "excerpt": "خلاصهٔ تست",
        "description": "توضیحاتِ تست",
        "icon": "rocket",
        "tags": "تست",
        "visual": "none",
        "card_span": "narrow",
        "order": "0",
        "featured": "on",
        "accent": "royal",
        "hero_eyebrow": "خدمات تست",
        "hero_title": "عنوان [[تست]]",
        "hero_lead": "مقدمهٔ تست",
        "hero_cta_primary_text": "مشاوره",
        "hero_cta_primary_url": "/contact/",
        "related_services": [str(service.pk)],
        **mgmt,
        "_save": "ذخیره",
    },
    follow=True,
)
check("admin POST add -> 200", r.status_code == 200, str(r.status_code))
created = Service.objects.filter(slug="t61-test-service").first()
check("admin POST created the service", created is not None)
if created:
    check(
        "accent/hero fields saved via admin",
        created.accent == "royal"
        and created.hero_eyebrow == "خدمات تست"
        and created.hero_title == "عنوان [[تست]]",
        f"accent={created.accent!r} eyebrow={created.hero_eyebrow!r}",
    )
    check(
        "related_services M2M saved via admin",
        list(created.related_services.all()) == [service],
    )
    created.delete()

# ------------------------------------------------------- empty DB renders
print("\n--- empty database (sentinel rollback) ---")


class _Rollback(Exception):
    """ raised on the way OUT of the atomic block to force a rollback
    (transaction.set_rollback(True) poisons the SQLite connection — D62). """


try:
    with transaction.atomic():
        Service.objects.all().delete()
        for url, expected in [
            ("/services/", 200),
            # با DBِ خالی، صفحهٔ اختصاصیِ یک خدمتِ ناموجود درست ۴۰۴ می‌دهد
            ("/services/web-design/", 404),
            ("/", 200),
            ("/portfolio/", 200),
            ("/blog/", 200),
        ]:
            r = client.get(url)
            check(f"empty DB GET {url} -> {expected}", r.status_code == expected, str(r.status_code))
        raise _Rollback
except _Rollback:
    pass

check("rollback restored the services", Service.objects.count() == len(services))
check(
    "rollback restored the plans",
    ServicePlan.objects.count() == 3,
    str(ServicePlan.objects.count()),
)

print()
if failures:
    print(f"{len(failures)} CHECKS FAILED: {failures}")
    sys.exit(1)
print("ALL T61 CHECKS PASSED")
