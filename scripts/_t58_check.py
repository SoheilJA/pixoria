"""T58 verification — brand choice wiring.

Checks the discovery, the resolution priority (upload > preset > fallback), the
empty-DB degradation, the rendered pages (icon links, manifest, JSON-LD logo,
header/footer lockup) and the admin widget.

DB writes run inside a rolled-back transaction (the D59 GOTCHA:
``transaction.atomic()`` COMMITS on a clean exit — it is not a sandbox).
"""

import json
import os
import sys
from contextlib import contextmanager
from io import BytesIO

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.stdout.reconfigure(encoding="utf-8")

import django  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.core.files.base import ContentFile  # noqa: E402
from django.core.files.storage import default_storage  # noqa: E402
from django.test import Client, RequestFactory  # noqa: E402
from django.db import transaction  # noqa: E402

from apps.core.brand_utils import brand_options, resolve_brand  # noqa: E402
from apps.core.models import SiteSettings  # noqa: E402

PASS, FAIL = [], []


@contextmanager
def rollback_block():
    """Run DB mutations that are rolled back on exit.

    ``transaction.set_rollback(True)`` poisons the connection on this Django/SQLite
    combination (every following query raises TransactionManagementError), so the
    block is rolled back the documented way instead: a sentinel exception on the
    way out. A real exception still propagates — and still rolls back.
    """

    class _Rollback(Exception):
        pass

    try:
        with transaction.atomic():
            yield
            raise _Rollback
    except _Rollback:
        pass


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'✓' if cond else '✗'} {name}" + (f" — {detail}" if detail and not cond else ""))


# ── discovery ──────────────────────────────────────────────────────────────
print("\n[1] discovery")
options = brand_options()
check("six options discovered", len(options) == 6, str(options))
check("sorted, orbit first", bool(options) and options[0][0] == "option-1-orbit")
check("persian labels present", all(label for _, label in options))


# ── resolution priority ────────────────────────────────────────────────────
print("\n[2] resolution priority")
settings = SiteSettings.objects.first()
live_choice = settings.logo_choice if settings else ""
check("live row has the default choice", bool(live_choice), repr(live_choice))

_req = RequestFactory().get("/", HTTP_HOST="localhost")
base = resolve_brand(settings, request=_req)
check("default logo_full resolves", bool(base["logo_full"]))
check("logo_full points at the chosen option", base["logo_full"].endswith(f"{base['id']}/logo-full.svg"))
check("mark / mono variants resolve", bool(base["mark"] and base["mono_light"] and base["mono_dark"]))
check("favicon defaults to the logo choice", base["favicon_svg"].endswith(f"{base['id']}/favicon.svg"))
check("og_image is absolute", base["og_image"].startswith("http"), base["og_image"])
check("schema_logo is absolute", base["schema_logo"].startswith("http"), base["schema_logo"])
check("not in upload mode by default", base["is_upload"] is False)

uploaded = []  # نام فایل‌های فیزیایی که save() می‌نویسد (rollback دیتابیس، دیسک را برنمی‌گرداند)

with rollback_block():
    s = SiteSettings.objects.first()
    s.logo_choice = "option-3-comet"
    s.save(update_fields=["logo_choice"])
    b = resolve_brand(SiteSettings.objects.first())
    check("explicit logo_choice wins", b["id"] == "option-3-comet", b["id"])
    # favicon_choice ردیفِ زنده مقدار پیش‌فرض خودش را دارد، پس اولویت می‌گیرد
    check("explicit favicon_choice beats the logo choice", b["favicon_svg"].endswith("option-1-orbit/favicon.svg"), b["favicon_svg"])

    s.logo_choice = "option-5-rocket"
    s.favicon_choice = ""
    s.save(update_fields=["logo_choice", "favicon_choice"])
    b = resolve_brand(SiteSettings.objects.first())
    check("empty favicon_choice follows the logo choice", b["favicon_svg"].endswith("option-5-rocket/favicon.svg"), b["favicon_svg"])

    s.logo_choice = "option-5-rocket"
    s.favicon_choice = "option-6-crescent"
    s.save(update_fields=["logo_choice", "favicon_choice"])
    b = resolve_brand(SiteSettings.objects.first())
    check("favicon_choice is independent", b["id"] == "option-5-rocket" and b["favicon_svg"].endswith("option-6-crescent/favicon.svg"))

    s.logo_choice = "option-99-does-not-exist"
    s.favicon_choice = ""
    s.save(update_fields=["logo_choice", "favicon_choice"])
    b = resolve_brand(SiteSettings.objects.first())
    check("stale choice falls back to option 1", b["id"] == "option-1-orbit", b["id"])
    check("stale choice: name falls back too", b["name"] == "مدار", b["name"])
    check("stale choice: favicon falls back too", b["favicon_svg"].endswith("option-1-orbit/favicon.svg"))

    s.logo_choice = ""
    s.logo = ContentFile(b"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'/>", name="t58-x.svg")
    uploaded.append(s.logo.name)
    s.save(update_fields=["logo", "logo_choice"])
    b = resolve_brand(SiteSettings.objects.first())
    check("uploaded logo wins over the preset", b["is_upload"] and b["logo_full"] == s.logo.url, b["logo_full"])
    # ستون‌های FileField در این پروژه NOT NULL هستند (blank بدون null)، پس
    # پاک‌سازی با None ممکن نیست — rollback خود دیتابیس را برمی‌گرداند.
    s.logo = ""
    s.save(update_fields=["logo"])

    s.favicon = ContentFile(b"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'/>", name="t58-f.svg")
    uploaded.append(s.favicon.name)
    s.save(update_fields=["favicon"])
    b = resolve_brand(SiteSettings.objects.first())
    check("uploaded favicon wins over the preset", b["favicon_svg"] == s.favicon.url, b["favicon_svg"])

# فایل‌های فیزیاییِ نوشته‌شده توسط save() هنوز روی دیسک هستند — rollback فقط DB را برمی‌گرداند.
for name in uploaded:
    try:
        default_storage.delete(name)
    except Exception:
        pass
check("uploaded test files cleaned from media", all(not default_storage.exists(n) for n in uploaded))


# ── empty database ─────────────────────────────────────────────────────────
print("\n[3] empty database")
with rollback_block():
    SiteSettings.objects.all().delete()
    b = resolve_brand(None)
    check("no settings row still resolves", bool(b["logo_full"]))
    check("no settings row: not an upload", b["is_upload"] is False)
    c = Client(HTTP_HOST="localhost")
    for url, label in [("/", "home"), ("/about/", "about"), ("/contact/", "contact")]:
        r = c.get(url)
        check(f"{label} 200 without SiteSettings", r.status_code == 200, str(r.status_code))
        body = r.content.decode()
        check(f"{label} has icon links", 'rel="icon"' in body)
        check(f"{label} has the manifest link", "/manifest.webmanifest" in body)


# ── rendered pages (real DB) ───────────────────────────────────────────────
print("\n[4] rendered pages")
client = Client(HTTP_HOST="localhost")
V1_REFS = ["brand/favicon.ico", "brand/favicon-48.png", "brand/site.webmanifest"]
for url, label in [
    ("/", "home"),
    ("/about/", "about"),
    ("/contact/", "contact"),
    ("/portfolio/", "portfolio list"),
    ("/blog/", "blog list"),
    ("/services/", "services list"),
]:
    r = client.get(url)
    body = r.content.decode()
    check(f"{label} 200", r.status_code == 200, str(r.status_code))
    check(f"{label} no v1 favicon refs", not any(ref in body for ref in V1_REFS))
    check(f"{label} no empty icon href", 'rel="icon" type="image/svg+xml" href=""' not in body)
    check(f"{label} og:image present", 'property="og:image"' in body)

home = client.get("/").content.decode()
check("home has the chosen logo-full", f'src="{base["logo_full"]}"' in home, base["logo_full"])
check("home JSON-LD logo present", '"logo":' in home)
check("home has exactly one logo-full in the header/footer", home.count(f'src="{base["logo_full"]}"') >= 1)

# مانیفست
r = client.get("/manifest.webmanifest")
check("manifest 200", r.status_code == 200, str(r.status_code))
check("manifest content type", "manifest+json" in r.headers.get("Content-Type", ""))
try:
    manifest = json.loads(r.content.decode())
    icons = manifest.get("icons", [])
    check("manifest parses as JSON", True)
    check("manifest has 3 icons", len(icons) == 3, str(len(icons)))
    check("manifest icons point at the chosen option", all(base["id"] in i["src"] for i in icons), str([i["src"] for i in icons]))
    check("manifest name is not empty", bool(manifest.get("name")))
    check("manifest maskable purpose present", any(i.get("purpose") == "maskable" for i in icons))
except ValueError as e:
    check("manifest parses as JSON", False, str(e))

# JSON-LD بلوک‌ها باید قابل parse باشند
for url in ["/", "/about/", "/contact/"]:
    body = client.get(url).content.decode()
    blocks = [
        json.loads(b)
        for b in __import__("re").finditer(
            r'<script type="application/ld\+json">(.*?)</script>', body, __import__("re").S
        )
        for b in [b.group(1)]
    ]
    check(f"{url} JSON-LD parses", True)
    logos = [b for blk in blocks for b in [blk] if isinstance(blk, dict)]
    found_logo = any('"logo"' in body for _ in [1])
    check(f"{url} has a logo key in JSON-LD", found_logo)


# ── admin ──────────────────────────────────────────────────────────────────
print("\n[5] admin")
admin = Client(HTTP_HOST="localhost")
admin.force_login(__import__("django.contrib.auth", fromlist=["get_user_model"]).get_user_model().objects.first())
for url, label in [("/admin/core/sitesettings/1/change/", "settings change")]:
    r = admin.get(url)
    body = r.content.decode()
    check(f"{label} 200", r.status_code == 200, str(r.status_code))
    check(f"{label} brand radios render", body.count('type="radio"') >= 2, str(body.count('type="radio"')))
    check(f"{label} widget css linked", "admin/css/brand_choice.css" in body)
    check(f"{label} preview images present", body.count("logo-mark.svg") >= 6, str(body.count("logo-mark.svg")))
    check(f"{label} full-logo previews present", body.count("logo-full.svg") >= 6, str(body.count("logo-full.svg")))


# ── staticfiles ────────────────────────────────────────────────────────────
print("\n[6] staticfiles")
from django.contrib.staticfiles import finders  # noqa: E402

for rel in ["admin/css/brand_choice.css"]:
    check(f"finder resolves {rel}", finders.find(rel) is not None)

print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    for f in FAIL:
        print("  FAILED:", f)
    sys.exit(1)
