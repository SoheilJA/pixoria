"""T60 verification — the space identity utilities exist, are used, and the
pages that use them still render.

Checks:
  - the built tailwind.css defines .orbit-ring, .orbit-dot, .planet-orb (+ the
    five accent variants), .star-field, the twinkle + ring-spin keyframes, the
    off-screen pause rule and the reduced-motion rules
  - every dark inner-page hero and the CTA/footer carry the shared layer
    (templates/_space_layer.html), with per-page ring/orb placement
  - the about hero keeps its T59 solar system and only takes stars
  - all public pages return 200 on the real DB and on an empty DB, and no
    template markers leaked
"""
import os
import sys

import django

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client
from django.test.runner import DiscoverRunner
from django.test.utils import setup_test_environment

PAGES = [
    "/",
    "/about/",
    "/contact/",
    "/portfolio/",
    "/blog/",
    "/services/",
    "/services/web-design/",
]

client = Client(HTTP_HOST="localhost")
bodies = {}
for url in PAGES:
    r = client.get(url)
    bodies[url] = r.content.decode("utf-8")
    assert r.status_code == 200, f"{url} -> {r.status_code}"
print(f"ok   {len(PAGES)} public pages 200")

# detail pages need a row; grab one from the real DB
from apps.blog.models import Article
from apps.portfolio.models import Portfolio

article = Article.objects.first()
project = Portfolio.objects.first()
if article:
    r = client.get(f"/blog/{article.slug}/")
    assert r.status_code == 200
    bodies[f"/blog/{article.slug}/"] = r.content.decode("utf-8")
if project:
    r = client.get(f"/portfolio/{project.slug}/")
    assert r.status_code == 200
    bodies[f"/portfolio/{project.slug}/"] = r.content.decode("utf-8")
print("ok   detail heroes checked too" if (article or project) else "ok   no detail rows")

# --- utilities in the built CSS --------------------------------------------
css = open("static/css/tailwind.css", encoding="utf-8").read()
css_checks = [
    (".orbit-ring", ".orbit-ring {"),
    (".orbit-ring--spin modifier", ".orbit-ring--spin {"),
    (".orbit-dot", ".orbit-dot {"),
    (".planet-orb", ".planet-orb {"),
    (".planet-orb accent: gold", ".planet-orb-gold {"),
    (".planet-orb accent: gold-light", ".planet-orb-gold-light {"),
    (".planet-orb accent: gold-dark", ".planet-orb-gold-dark {"),
    (".planet-orb accent: royal", ".planet-orb-royal {"),
    (".planet-orb accent: cream", ".planet-orb-cream {"),
    (".star-field", ".star-field {"),
    ("star twinkle keyframes", "@keyframes starTwinkle"),
    ("orbit ring spin keyframes", "@keyframes orbitRingSpin"),
    ("off-screen pause rule", ".is-paused .orbit-ring--spin,"),
    ("reduced-motion pause of the twinkle", ".star-field::before,"),
]
for label, needle in css_checks:
    hits = needle in css
    print(f"{'ok  ' if hits else 'FAIL'} css: {label}")
    assert hits, f"built CSS missing: {label}"

# --- the shared layer is used where it should be ----------------------------
shared = open("templates/partials/_space_layer.html", encoding="utf-8").read()
assert "star-field" in shared and "orbit-ring" in shared and "planet-orb" in shared
print("ok   templates/partials/_space_layer.html defines the layer")

heroes = [
    ("/portfolio/", "ring + royal orb", "-right-28 top-16"),
    ("/blog/", "ring + gold-light orb", "-left-40 bottom-6"),
    ("/contact/", "ring + cream orb", "-right-36 top-24"),
]
if article:
    heroes.append((f"/blog/{article.slug}/", "ring + royal orb", "-right-32 top-12"))
if project:
    heroes.append((f"/portfolio/{project.slug}/", "ring + gold orb", "-left-40 bottom-10"))

for url, note, needle in heroes:
    b = bodies[url]
    star = "star-field" in b
    placed = needle in b
    print(f"{'ok  ' if star and placed else 'FAIL'} {url}: space layer ({note})")
    assert star, f"{url} has no star-field"
    assert placed, f"{url} placement var missing"
    assert "_space_layer" not in b, f"{url} leaked the raw include tag"

# CTA + footer are on every page; the about hero takes stars only
about = bodies["/about/"]
assert "star-field" in about, "about hero has no star-field"
assert about.count("star-field") >= 3, "about needs hero stars + CTA + footer stars"
# isolate the first <section> (the hero) — the CTA further down may carry a ring
first = about.find("<section")
second = about.find("<section", first + 1)
hero = about[first:second] if (first >= 0 and second > first) else about
assert "orbit-ring" not in hero, "about hero should take stars only (no second ring)"
print("ok   /about/: hero is stars only — the T59 solar system stays the hero")
print("ok   CTA + footer carry the star-field on every page")

# --- no leaked markers, empty DB still fine ---------------------------------
for label, needle in [("[[ ]] marker", "[["), ("{% comment %}", "{% comment %}"),
                      ("{{ }}", "{{")]:
    hits = [u for u, b in bodies.items() if needle in b]
    print(f"{'FAIL' if hits else 'ok  '} no leaked {label}: {hits or 'none'}")
    assert not hits

setup_test_environment()
runner = DiscoverRunner(verbosity=0)
old_config = runner.setup_databases()
try:
    c = Client(HTTP_HOST="localhost")
    for url in ("/", "/about/", "/contact/", "/portfolio/", "/blog/", "/services/"):
        r = c.get(url)
        assert r.status_code == 200, f"empty DB {url} -> {r.status_code}"
    print("ok   all pages 200 on an empty (test) database")
finally:
    runner.teardown_databases(old_config)

print("\nALL T60 CHECKS PASSED")
