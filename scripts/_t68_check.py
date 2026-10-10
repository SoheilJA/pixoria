"""T68 — بررسیِ اتمسفرِ مختصِ هر خدمت.

هر یک از چهار خدماتِ موجود باید موتیفِ مختصِ همان ``visual`` را در هیرویش
داشته باشد و هیچ کدام نباید صفحه را بشکند. تمامِ چک‌ها روی دیتابیسِ واقعی
انجام می‌شود (فقط خواندنی).
"""

import os
import sys

import django

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client  # noqa: E402
from django.template.loader import get_template  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

client = Client(HTTP_HOST="localhost")
VISUALS = {
    "web-design": ("browser", ["svc-blueprint", "svc-device", "svc-chip"]),
    "programming": ("terminal", ["svc-glyph", "svc-type"]),
    "logo-design": ("diamond", ["svc-tick", "svc-logo-draw", "svc-chip"]),
    "graphic-design": ("palette", ["svc-swatch", "svc-drip"]),
}
ok = True


def check(cond, label):
    global ok
    if not cond:
        ok = False
    print(("  ✓ " if cond else "  ✗ ") + label)


for slug, (visual, motifs) in VISUALS.items():
    print(f"\n─ /services/{slug}/ (visual={visual})")
    res = client.get(f"/services/{slug}/")
    check(res.status_code == 200, f"status 200 (got {res.status_code})")
    body = res.content.decode("utf-8")
    check(f'service-theme-{visual}' in body, f"wrapper service-theme-{visual}")
    for motif in motifs:
        check(motif in body, f"موتیفِ {motif}")
    check("{#" not in body, "بدون نشتِ کامنتِ قالب")
    check("[[" not in body, "بدون نشتِ نشانِ هایلایت")
    check("cdn." not in body, "بدون ارجاعِ CDN")
    #data-pause روی هیرو
    check("data-pause" in body, "data-pause روی هیرو")

print("\n─ صفحاتِ دیگر")
for url in ["/", "/about/", "/contact/", "/portfolio/", "/blog/", "/services/"]:
    res = client.get(url)
    check(res.status_code in (200, 404), f"{url} → {res.status_code}")

print("\n─ قالب با دیتابیسِ خالی")
from django.test.utils import setup_test_environment  # noqa: E402
from django.db import transaction  # noqa: E402

setup_test_environment()
try:
    with transaction.atomic():
        from apps.services.models import Service  # noqa: E402

        Service.objects.all().delete()
        res = client.get("/services/")
        check(res.status_code == 200, f"لیست با DB خالی 200 ({res.status_code})")
        res = client.get("/services/web-design/")
        check(res.status_code == 404, f"جزئیاتِ خدمتِ حذف‌شده 404 ({res.status_code})")
        raise RuntimeError("rollback")
except RuntimeError:
    pass

print("\n" + ("همهٔ چک‌ها گذشت ✓" if ok else "برخی چک‌ها شکست خوردند ✗"))
sys.exit(0 if ok else 1)
