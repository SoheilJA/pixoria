"""T59 verification — about hero is now an animated solar system.

Checks the rendered /about/ page (real DB, empty DB and 1-6 services):
  - the old "orbit pills" artwork is gone (glass pills, spin-slow ring, brand
    mark floating in the middle of plain rings)
  - the new solar system markup is there: sun, one orbit ring + planet link per
    service (label chip included), three debris dots, data-pause hook
  - planets link to their service detail page and carry the service title
  - the built tailwind.css holds the motion rules (offset-path + counter-tilt +
    pause + reduced-motion) so the markup is not depending on dead CSS
  - every page still returns 200 and no template markers leaked
"""
import os
import re
import sys

import django

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client
from django.test.runner import DiscoverRunner
from django.test.utils import setup_test_environment
from django.db import transaction

from apps.services.models import Service

client = Client(HTTP_HOST="localhost")
about = client.get("/about/").content.decode("utf-8")
print(f"{client.get('/about/').status_code} /about/ ({len(about)} B)")

# --- old artwork gone -------------------------------------------------------
old = [
    ("orbit pill (glass service capsule)", "glass absolute flex items-center gap-2 rounded-full px-5 py-2.5"),
    ("spin-slow ring", "spin-slow"),
    ("static ring stack", "rounded-full border border-dashed border-gold/30"),
    ("floating brand mark", 'partials/_brand_mark.html" with class="h-12 w-12"'),
]
for label, needle in old:
    hits = needle in about
    print(f"{'FAIL' if hits else 'ok  '} old artwork removed — {label}")
    assert not hits, f"old artwork still on /about/: {label}"

# --- new artwork present ----------------------------------------------------
services = list(Service.objects.all())
n = len(services)
checks = [
    ("ss-system stage", about.count("ss-system")),
    ("ss-plane (tilted orbit plane)", about.count("ss-plane")),
    ("ss-sun", about.count("ss-sun")),
    ("ss-orbit groups", about.count('class="ss-orbit"')),
    ("ss-ring", about.count('class="ss-ring"')),
    ("ss-planet links", about.count('class="ss-planet ')),
    ("ss-label chips", about.count('class="ss-label"')),
    ("ss-debris", about.count("ss-debris ss-a-")),
    ("data-pause hook", about.count("data-pause")),
]
for label, count in checks:
    print(f"{'ok  ' if count else 'FAIL'} {label}: {count}")
    assert count, f"{label} missing on /about/"

assert about.count('class="ss-planet ') == n, "one planet per service expected"
assert about.count('class="ss-ring"') == n, "one ring per service expected"
assert about.count('class="ss-orbit"') == n + 3, "orbits = services + 3 debris belts"
assert about.count("data-pause") == 1, "the system is the only paused element"
print(f"ok   {n} services -> {n} planets + {n} rings + 3 debris orbits")

# planets link to their detail page and carry the service title
for service in services:
    link = f'href="/services/{service.slug}/"'
    assert link in about, f"planet link missing for {service.slug}"
    assert f">{service.title}</span>" in about, f"label missing for {service.slug}"
print("ok   every planet links to its service page with its title as the label")

# no service count dependency baked into the template beyond the 6-planet cap
assert "--size:3rem" in about, "per-planet sizing vars not rendered"
assert "--dur:30s" in about and "--dir:reverse" in about, "speed/direction vars missing"
assert "--d:12%" in about, "static (reduced-motion) position var missing"

# --- CSS actually carries the motion rules ----------------------------------
css = open("static/css/tailwind.css", encoding="utf-8").read()
css_checks = [
    ("offset-path ellipse for planets/debris", "offset-path: ellipse("),
    ("labels never rotate", "offset-rotate: 0deg"),
    ("orbit plane tilt", "--ss-tilt"),
    ("counter-tilt for planet content", "calc(var(--ss-tilt) * -1)"),
    ("container query units resolve against the stage", "1cqw"),
    ("pause-offscreen rule", ".ss-system.is-paused"),
    ("reduced-motion static spread", ".ss-debris {\n    offset-distance: var(--d, 0%) !important;"),
    ("sun pulse keyframes", "@keyframes ssSunPulse"),
    ("travel keyframes", "@keyframes ssTravel"),
]
for label, needle in css_checks:
    hits = needle in css
    print(f"{'ok  ' if hits else 'FAIL'} css: {label}")
    assert hits, f"built CSS is missing: {label}"

# --- other pages untouched --------------------------------------------------
for url in ("/", "/contact/", "/portfolio/", "/blog/", "/services/",
            "/services/web-design/"):
    r = client.get(url)
    assert r.status_code == 200, f"{url} -> {r.status_code}"
print("ok   all public pages still 200")

for label, needle in [("[[ ]] marker", "[["), ("{% comment %}", "{% comment %}"),
                      ("{{ }}", "{{")]:
    assert needle not in about, f"leaked template marker on /about/: {label}"
print("ok   no leaked template markers on /about/")

# --- empty database + 1..6 services (throwaway test DB) ---------------------
setup_test_environment()
runner = DiscoverRunner(verbosity=0)
old_config = runner.setup_databases()
try:
    with transaction.atomic():
        # the whole hero (solar system included) is guarded by {% if hero %}
        from apps.core.models import AboutPageHero

        AboutPageHero.objects.create(
            title="دربارهٔ ما", description="تست", cta_primary_text="تماس"
        )

        Service.objects.all().delete()
        c = Client(HTTP_HOST="localhost")
        r = c.get("/about/")
        assert r.status_code == 200
        b = r.content.decode("utf-8")
        # no services -> the solar-system nav is guarded out, the hero stays
        assert 'class="ss-planet ' not in b, "empty DB should render no planets"
        assert "ss-sun" not in b, "empty DB should render no solar system at all"
        print("ok   empty DB: /about/ 200, solar system hidden (guarded)")

        for count in range(1, 7):
            Service.objects.all().delete()
            for i in range(count):
                Service.objects.create(
                    title=f"خدمت تست {i + 1}",
                    slug=f"test-service-{i + 1}",
                    excerpt="تست",
                    description="تست",
                    icon="sparkles",
                )
            r = c.get("/about/")
            b = r.content.decode("utf-8")
            planets = b.count('class="ss-planet ')
            rings = b.count('class="ss-ring"')
            assert r.status_code == 200 and planets == count and rings == count, (
                f"{count} services -> {planets} planets, {rings} rings"
            )
        print("ok   1..6 services: planet/ring count always matches, page 200")
finally:
    runner.teardown_databases(old_config)

print("\nALL T59 CHECKS PASSED")
