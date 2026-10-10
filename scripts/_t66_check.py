"""T66 verification: the pricing section on the service detail pages + the
contact-form prefill from the plan CTAs.

Run:  venv/Scripts/python scripts/_t66_check.py
"""
import os
import subprocess
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
from django.test import Client  # noqa: E402
from django.test.utils import override_settings  # noqa: E402
from django.db import transaction  # noqa: E402

django.setup()

from apps.services.models import Service, ServicePlan  # noqa: E402
from apps.contact.models import SubjectChoice, ContactSubmission  # noqa: E402
from apps.core.templatetags.fa_digits import fa_price  # noqa: E402

H = {"HTTP_HOST": "localhost"}
ok = True

# همان ثابت‌های apps/contact/views.py — موضوعِ پیش‌پر شده.
ORDER = "درخواست سفارش پروژه"
SERVICE = "مشاورهٔ خدمات"


def check(cond, label):
    global ok
    if not cond:
        ok = False
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


class Sentinel(Exception):
    """برای برگرداندنِ تراکنش در تست‌های دیتابیسِ خالی."""


print("== service detail pages ==")
c = Client(**H)
for s in Service.objects.all():
    with override_settings(DEBUG=False):
        r = c.get(f"/services/{s.slug}/")
    body = r.content.decode("utf-8", "replace")
    plans = list(s.plans.filter(is_active=True))
    print(f"-- {s.slug} ({r.status_code}, {len(plans)} plans)")
    check(r.status_code == 200, "status 200")
    check(("تعرفهٔ" in body) == bool(plans), "header only with plans")
    check(body.count("محبوب‌ترین") == sum(1 for p in plans if p.is_featured),
          "one badge per featured plan")
    check(body.count("data-custom-root") == (1 if s.custom_items.exists() else 0),
          "custom block only with custom items")
    for p in plans:
        slug_q = f"?plan={p.plan_type}&amp;service={s.slug}"
        check(slug_q in body or bool(p.cta_url), f"cta query for {p.name}")
        if p.price:
            check(fa_price(p.price) in body, f"price formatted for {p.name}")
        else:
            check((p.price_note or "تماس بگیرید") in body, f"price note for {p.name}")
        check(f">{p.name}<" in body, f"plan name rendered")
        # ویژگیِ شامل‌شده تیکِ طلایی دارد، شامل‌نشده ضربدرِ کمرنگ.
        for f in p.features.all():
            marker = "text-gold-dark" if f.included else "text-coy/55"
            check(f.title[:24] in body and marker in body,
                  f"feature row ({f.title[:24]})")
    for item in s.custom_items.all():
        check(f">{item.title}<" in body, f"custom item {item.title}")
        check(f'data-custom-price="{item.price}"' in body,
              f"custom item price hook {item.title}")
    check("[[" not in body, "no [[ leak")
    check("{#" not in body and "{% comment" not in body, "no comment leak")

print("== plan CTA prefill on the contact form ==")
s = Service.objects.first()
plan = s.plans.first()
for url, note in [
    (f"/contact/?service={s.slug}", "service only"),
    (f"/contact/?plan={plan.plan_type}&service={s.slug}", "service + plan"),
    (f"/contact/?plan=nope&service={s.slug}", "bad plan"),
    (f"/contact/?service=no-such-service", "bad service"),
    (f"/contact/?plan={plan.plan_type}", "plan without service"),
    ("/contact/", "no params"),
]:
    with override_settings(DEBUG=False):
        r = c.get(url)
    body = r.content.decode("utf-8", "replace")
    selected = [ln.strip() for ln in body.splitlines() if "selected" in ln]
    print(f"-- {note}")
    check(r.status_code == 200, "status 200")
    if "bad" in note:
        check("در حالِ مشاوره" not in body, "no prefill note")
    if note == "service + plan":
        check(plan.name in body, "plan name in note/message")
        check(any(ORDER in ln for ln in selected), "order subject selected")
        check("درخواستِ مشاوره برای" in body, "message prefilled")
    if note == "service only":
        check(any(SERVICE in ln for ln in selected), "consult subject selected")
    if note == "plan without service":
        check(any(ORDER in ln for ln in selected), "order subject without service")
    if note == "no params":
        check(not any(ORDER in ln or SERVICE in ln for ln in selected),
              "nothing preselected")
        check("در حالِ مشاوره" not in body, "no prefill note")

print("== prefill survives a real POST ==")
with transaction.atomic():
    try:
        subject = (SubjectChoice.objects.filter(label=ORDER).first()
                   or SubjectChoice.objects.first())
        payload = {
            "name": "تست کاربر",
            "email": "t66@example.com",
            "subject": subject.label,
            "message": "پیامِ تستیِ کافی برای عبور از حداقل طول.",
            "company_website": "",
        }
        n0 = ContactSubmission.objects.count()
        with override_settings(DEBUG=False):
            r = c.post(f"/contact/?plan={plan.plan_type}&service={s.slug}",
                       payload, **H)
        check(r.status_code == 200, "post 200")
        check(ContactSubmission.objects.count() == n0 + 1, "submission saved")
        sub = ContactSubmission.objects.latest("id")
        check(sub.subject == subject.label, "subject stored")
        check(sub.message == payload["message"], "message stored")
        # هانی‌پات: ذخیره نمی‌شود ولی موفقیت نشان داده می‌شود.
        payload["company_website"] = "spam"
        with override_settings(DEBUG=False):
            c.post(f"/contact/?plan={plan.plan_type}&service={s.slug}",
                   payload, **H)
        check(ContactSubmission.objects.count() == n0 + 1, "honeypot saved nothing")
        raise Sentinel
    except Sentinel:
        transaction.set_rollback(True)

print("== empty database (rolled back) ==")
with transaction.atomic():
    try:
        ServicePlan.objects.all().delete()
        with override_settings(DEBUG=False):
            r = c.get(f"/services/{s.slug}/")
        body = r.content.decode("utf-8", "replace")
        print("-- no plans")
        check(r.status_code == 200, "status 200")
        check("تعرفهٔ" not in body, "pricing section absent")
        check("قیمت‌گذاری" not in body, "eyebrow absent")
        check("data-custom-root" not in body, "custom block absent")
        check("data-custom-total" not in body, "calculator total absent")
        with override_settings(DEBUG=False):
            r2 = c.get("/contact/?plan=pro&service=web-design")
        check(r2.status_code == 200, "contact still 200 with stale link")
        raise Sentinel
    except Sentinel:
        transaction.set_rollback(True)

print("== other pages unaffected ==")
for url, name in [("/", "home"), ("/about/", "about"), ("/contact/", "contact"),
                  ("/portfolio/", "portfolio"), ("/blog/", "blog"),
                  ("/services/", "services list")]:
    with override_settings(DEBUG=False):
        r = c.get(url)
    check(r.status_code == 200, f"{name} 200")

print("== syntax + checks ==")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
py = sys.executable
for cmd, label in [
    ([py, "manage.py", "check"], "manage.py check"),
    ([py, "manage.py", "makemigrations", "--check", "--dry-run"],
     "makemigrations --check"),
]:
    res = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    check(res.returncode == 0,
          f"{label} ({(res.stdout + res.stderr).strip()[:100]})")

# pixoria.js یک ES module است و package.json ریشه module نیست، پس --check
# مستقیم روی فایل کار نمی‌کند؛ از stdin با --input-type=module استفاده می‌کنیم.
with open(os.path.join(root, "static", "js", "pixoria.js"), "rb") as fh:
    node = subprocess.run(["node", "--input-type=module", "--check"],
                          stdin=fh, capture_output=True, text=True, cwd=root)
check(node.returncode == 0, f"pixoria.js syntax ({node.stderr.strip()[:100]})")

print("\nRESULT:", "ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
