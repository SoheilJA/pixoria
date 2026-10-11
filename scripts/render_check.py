"""T41 verification: render every live page with the current DB.

Run:  venv/Scripts/python scripts/render_check.py
"""
import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
from django.conf import settings  # noqa: E402
from django.test import Client  # noqa: E402
from django.test.utils import override_settings  # noqa: E402

django.setup()

H = {"HTTP_HOST": "localhost"}
pages = [
    ("/", "home"),
    ("/about/", "about"),
    ("/contact/", "contact"),
    ("/portfolio/", "portfolio list"),
    ("/blog/", "blog list"),
    ("/login/", "login"),
    ("/who-are-you/login/", "admin login"),
    ("/services/", "services list"),
    ("/does-not-exist-xyz/", "404"),
]

c = Client(**H)
for url, name in pages:
    try:
        with override_settings(DEBUG=False):
            r = c.get(url)
        extra = ""
        if r.status_code == 200:
            body = r.content.decode("utf-8", "replace")
            leaks = [t for t in ("[[", "cdn.tailwindcss", "cdn.jsdelivr", "googleapis")
                      if t in body]
            extra = f" {len(body)//1024}KB" + (f" LEAKS:{leaks}" if leaks else " clean")
        print(f"{name:16} {url:24} -> {r.status_code}{extra}")
    except Exception as exc:  # noqa: BLE001
        print(f"{name:16} {url:24} -> EXC {type(exc).__name__}: {exc}")

# detail pages need slugs
from apps.portfolio.models import Portfolio
from apps.blog.models import Article
from apps.services.models import Service

for slug in Portfolio.objects.values_list("slug", flat=True)[:2]:
    r = c.get(f"/portfolio/{slug}/", **H)
    print(f"{'portfolio dtl':16} /portfolio/{slug}/ -> {r.status_code}")
if not Portfolio.objects.exists():
    print("portfolio dtl   (no Portfolio rows in DB)")

for slug in Article.objects.values_list("slug", flat=True)[:2]:
    r = c.get(f"/blog/{slug}/", **H)
    print(f"{'blog dtl':16} /blog/{slug}/ -> {r.status_code}")
if not Article.objects.exists():
    print("blog dtl        (no Article rows in DB)")

for slug in Service.objects.values_list("slug", flat=True)[:2]:
    r = c.get(f"/services/{slug}/", **H)
    print(f"{'service dtl':16} /services/{slug}/ -> {r.status_code}")
if not Service.objects.exists():
    print("service dtl     (no Service rows in DB)")
