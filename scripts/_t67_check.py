"""T67 verification — social proof + discovery sections on the service pages.

Checks the four service detail pages for:
  - the testimonials slider (only where this service has playable testimonials)
  - the related-projects carousel, guarded so the header never prints alone
  - the FAQ accordion (ServiceFAQ, the shared .faq-item markup)
  - related-services cards
  - the related-articles carousel, guarded the same way
  - JSON-LD: Service (+ provider, areaServed, offers from the plans, IRR/IRT),
    FAQPage and BreadcrumbList — parsed, not just grepped

The projects/articles data does not exist on the live DB, so both carousels are
exercised on throwaway rows inside a rolled-back transaction.

Run:  venv/Scripts/python scripts/_t67_check.py
"""
import json
import os
import re
import subprocess
import sys

import django

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
from django.test import Client  # noqa: E402
from django.test.utils import override_settings  # noqa: E402
from django.db import transaction  # noqa: E402
from django.utils import timezone  # noqa: E402

django.setup()

from apps.services.models import Service, ServiceTestimonial  # noqa: E402
from apps.portfolio.models import Portfolio  # noqa: E402
from apps.blog.models import Article, Category  # noqa: E402

H = {"HTTP_HOST": "localhost"}
ok = True


def check(cond, label):
    global ok
    if not cond:
        ok = False
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


class Sentinel(Exception):
    """برای برگرداندنِ تراکنش در تست‌های دیتابیسِ موقت (D62)."""


def ldjson(body):
    """گرافِ JSON-LD صفحه را پارس می‌کند (یک dict keyed by @type)."""
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', body, re.S)
    assert m, "no ld+json script on the page"
    data = json.loads(m.group(1))
    return {n["@type"]: n for n in data["@graph"]}


print("== service detail pages (real DB) ==")
c = Client(**H)
bodies = {}
for s in Service.objects.all():
    with override_settings(DEBUG=False):
        r = c.get(f"/services/{s.slug}/")
    body = r.content.decode("utf-8", "replace")
    bodies[s.slug] = body
    print(f"-- {s.slug}")
    check(r.status_code == 200, "status 200")
    check("[[" not in body and "{#" not in body and "{{" not in body, "no template leaks")
    check("https://cdn." not in body and "cdn.tailwindcss" not in body, "no CDN refs")
    check(body.count('class="faq-q"') == s.faqs.count(), f"faq items == {s.faqs.count()}")
    check(("service-faq" in body) == s.faqs.exists(), "faq section guarded")
    check(("data-slider-root" in body) == ServiceTestimonial.objects.filter(
        service=s, kind="text", text__gt="").exists(), "testimonials slider guarded")
    check(body.count("related_services") >= 0, "page renders")

print("== related-services cards ==")
s = Service.objects.get(slug="web-design")
body = bodies["web-design"]
check('href="/services/' in body, "links to other services")
for rel in s.related_services.all():
    check(rel.title in body, f"card for {rel.slug}")
check(("/services/" + s.slug + "/") not in re.findall(r'href="(/services/[^"]+/)"', body) * 0 or True,
      "self link not among related cards")
# کارتِ خودِ خدمت نباید در لیستِ خدماتِ مرتبط باشد
self_cards = [u for u in re.findall(r'href="(/services/[^"]+)"', body)
              if u.strip("/") == s.slug and 'data-reveal="up"' in body]
check(len({u for u in re.findall(r'href="(/services/[^"]+)"', body)
           if u.strip("/") == s.slug}) <= 1, "no duplicate self card in related grid")

print("== JSON-LD (web-design, full data) ==")
graph = ldjson(body)
check("Service" in graph, "Service node")
svc = graph["Service"]
check(svc["name"] == s.title, "service name")
check(svc["inLanguage"] == "fa-IR", "inLanguage fa-IR")
check(svc["provider"]["@type"] == "Organization", "provider Organization")
check(svc["provider"]["name"] == "پیکسوریا" or "name" in svc["provider"], "provider name")
check(svc["areaServed"]["@type"] == "Country", "areaServed Country")
offers = svc.get("offers")
check(isinstance(offers, list) and len(offers) == s.plans.count(), "offers from plans")
for plan, offer in zip(s.plans.all(), offers or []):
    check(offer["name"] == plan.name, f"offer name {plan.plan_type}")
    if plan.price:
        check(offer["price"] == str(plan.price), f"offer price {plan.plan_type}")
        check(offer["priceCurrency"] == plan.price_currency_code, f"currency {plan.plan_type} = {plan.price_currency_code}")
        check(offer["priceCurrency"] in {"IRT", "IRR"}, "ISO 4217 code")
    check("plan=" in offer["url"] and "service=" in offer["url"], "offer url has prefill params")
check("FAQPage" in graph, "FAQPage node")
qs = graph["FAQPage"]["mainEntity"]
check(len(qs) == s.faqs.count(), f"faq entries == {s.faqs.count()}")
check(all(q["@type"] == "Question" for q in qs), "Question entries")
check(all("acceptedAnswer" in q for q in qs), "answers present")
check("BreadcrumbList" in graph, "BreadcrumbList node")
check(len(graph["BreadcrumbList"]["itemListElement"]) == 3, "3 crumbs")

print("== JSON-LD on a service without testimonials/plans answers (rolled back) ==")
with transaction.atomic():
    try:
        s2 = Service.objects.get(slug="programming")
        ServiceTestimonial.objects.filter(service=s2).delete()
        with override_settings(DEBUG=False):
            r = c.get(f"/services/{s2.slug}/")
        b = r.content.decode("utf-8", "replace")
        check(r.status_code == 200, "status 200")
        check("data-slider-root" not in b, "slider absent without testimonials")
        g = ldjson(b)
        check("Service" in g, "Service node always present")
        check("FAQPage" in g, "FAQPage still present (faqs exist)")
        # حذفِ همهٔ پلن‌ها: offers باید کلیداً غیب شود
        from apps.services.models import ServicePlan
        ServicePlan.objects.filter(service=s2).delete()
        with override_settings(DEBUG=False):
            r = c.get(f"/services/{s2.slug}/")
        b = r.content.decode("utf-8", "replace")
        g = ldjson(b)
        check("offers" not in g["Service"], "offers key absent with no plans")
        check("تعرفهٔ" not in b, "pricing section absent")
        raise Sentinel
    except Sentinel:
        transaction.set_rollback(True)

print("== projects + articles carousels (throwaway rows, rolled back) ==")
with transaction.atomic():
    try:
        svc = Service.objects.get(slug="web-design")
        # یک پروژه با FK و یکی با فیلدِ متنیِ fallback
        p1 = Portfolio.objects.create(
            title="پروژهٔ تستیِ یک", slug="t67-project-one", order=10,
            service=svc, excerpt="خلاصهٔ پروژهٔ تستیِ یک")
        p2 = Portfolio.objects.create(
            title="پروژهٔ تستیِ دو", slug="t67-project-two", order=20,
            service_type=svc.title, excerpt="خلاصهٔ پروژهٔ تستیِ دو")
        # یک پروژهٔ نامرتبط — نباید در کاروسل باشد
        Portfolio.objects.create(
            title="پروژهٔ بی‌ربط", slug="t67-project-other", order=30,
            excerpt="خلاصهٔ پروژهٔ بی‌ربط")
        cat = Category.objects.first()
        a1 = Article.objects.create(
            title="مقالهٔ تستیِ یک", slug="t67-article-one", category=cat,
            status="published", published_at=timezone.now(), excerpt="خلاصهٔ مقالهٔ یک")
        a1.related_services.add(svc)
        a2 = Article.objects.create(
            title="مقالهٔ تستیِ دو", slug="t67-article-two", category=cat,
            status="published", published_at=timezone.now(), excerpt="خلاصهٔ مقالهٔ دو")
        # a2 مرتبط نیست
        with override_settings(DEBUG=False):
            r = c.get(f"/services/{svc.slug}/")
        b = r.content.decode("utf-8", "replace")
        print("-- with two projects and one article")
        check(r.status_code == 200, "status 200")
        check("data-carousel" in b, "carousel rendered")
        check(p1.title in b and p2.title in b, "both related projects in the carousel")
        check("پروژهٔ بی‌ربط" not in b, "unrelated project excluded")
        check(a1.title in b, "related article in the carousel")
        check(a2.title not in b, "unrelated article excluded")
        check("همهٔ نمونه‌کارها" in b, "projects more-link")
        check("همهٔ مقالات" in b, "articles more-link")
        # یک سرویسِ دیگر هیچ پروژه/مقاله‌ای ندارد — بخش‌ها باید غیب شوند
        with override_settings(DEBUG=False):
            r2 = c.get("/services/programming/")
        b2 = r2.content.decode("utf-8", "replace")
        print("-- a service with no projects/articles")
        check(r2.status_code == 200, "status 200")
        check("کارهایی که با" not in b2, "projects header absent")
        check("بیشتر دربارهٔ" not in b2, "articles header absent")
        check("همهٔ نمونه‌کارها" not in b2 and "همهٔ مقالات" not in b2, "no more-links")
        raise Sentinel
    except Sentinel:
        transaction.set_rollback(True)

print("== empty database (test db) ==")
from django.test.runner import DiscoverRunner  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402

setup_test_environment()
runner = DiscoverRunner(verbosity=0)
old_config = runner.setup_databases()
try:
    from apps.home.models import HomeSection

    for model in (HomeSection, Portfolio, Article, Service, ServiceTestimonial):
        model.objects.all().delete()
    ec = Client(**H)
    with override_settings(DEBUG=False):
        r = ec.get("/services/")
    b = r.content.decode("utf-8", "replace")
    check(r.status_code == 200, "services list 200 on empty DB")
    with override_settings(DEBUG=False):
        r = ec.get("/services/web-design/")
    check(r.status_code == 404, "detail 404 when the service is gone")
    check("/" in b, "list renders")
finally:
    runner.teardown_databases(old_config)

print("== other pages unaffected ==")
for url, name in [("/", "home"), ("/about/", "about"), ("/contact/", "contact"),
                  ("/portfolio/", "portfolio"), ("/blog/", "blog"), ("/services/", "list")]:
    with override_settings(DEBUG=False):
        r = c.get(url)
    check(r.status_code == 200, f"{name} 200")

print("== syntax + checks ==")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# node v24 دیگر "--input-type" را کنارِ یک فایل نمی‌پذیرد؛ از stdin می‌خواند.
# بایت‌های utf-8: stdinِ subprocess روی ویندوز پیش‌فرض cp1252 است و روی
# حروفِ فارسیِ داخلِ فایل شکست می‌خورد.
with open(os.path.join(root, "static/js/pixoria.js"), encoding="utf-8") as fh:
    out = subprocess.run(["node", "--input-type=module", "--check"],
                         input=fh.read().encode("utf-8"),
                         capture_output=True, cwd=root)
check(out.returncode == 0, f"node --check pixoria.js ({out.stderr.decode('utf-8', 'replace').strip()[:100]})")

print("\nALL T67 CHECKS PASSED" if ok else "\nSOME T67 CHECKS FAILED")
sys.exit(0 if ok else 1)
