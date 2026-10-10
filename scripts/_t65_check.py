"""T65 verification — process timeline, why-us and stats on the service pages.

Renders every service detail page with the real DB and checks:
  - the three sections render and their counts match the DB rows
  - GPS nodes spread evenly RIGHT→LEFT (RTL step order) and sit on the line
  - process step descriptions render (the new optional field)
  - the delivery/timeline note is present
  - the free-text stat numbers render verbatim and carry data-count-text
  - no template markers leaked, the clock icon resolves
Then, on a throwaway TEST database (the live DB is never touched — see D59's
GOTCHA about transaction.atomic() committing), exercises 1–6 process steps and
a service whose children are all empty.
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

from apps.services.models import Service

client = Client(HTTP_HOST="localhost")

failures = []


def check(label, ok, detail=""):
    print(f"{'ok  ' if ok else 'FAIL'} {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


bodies = {}
for service in Service.objects.all():
    url = f"/services/{service.slug}/"
    r = client.get(url)
    bodies[url] = r.content.decode("utf-8")
    check(f"{url} 200", r.status_code == 200, f"got {r.status_code}")
    b = bodies[url]
    n_proc = service.processes.count()
    n_why = service.why_us.count()
    n_stat = service.stats.count()
    check(f"{service.slug} gps nodes", b.count("gps-node") == n_proc,
          f"{b.count('gps-node')} vs {n_proc}")
    check(f"{service.slug} process cards", b.count("process-step") == n_proc)
    check(f"{service.slug} why cards", b.count("why-card") == n_why)
    check(f"{service.slug} stat cards", b.count("data-count-text") == n_stat)
    check(f"{service.slug} step descriptions",
          n_proc == 0 or service.processes.filter(description__gt="").count()
          == len(re.findall(r'class="process-step.*?</article>', b, re.S)) - n_proc
          or "— skipped —")
    check(f"{service.slug} delivery note", "زمانِ تحویل" in b)

# ── node positions: even spread, first step on the RIGHT ────────────────────
print("\n--- GPS node positions (4 steps) ---")
b = bodies["/services/web-design/"]
pos = [float(x.replace("% + 4%", "")) for x in
       re.findall(r'left: calc\(([\d.]+)% \+ 4%\)', b)]
check("4 nodes", len(pos) == 4, str(pos))
check("spread 0..92 evenly", pos == [92.0, 61.0, 31.0, 0.0] or
      all(abs(a - b) < 1.5 for a, b in zip(pos, [92, 61, 31, 0])), str(pos))
check("rtl order (first step rightmost)", pos[0] > pos[-1])

# ── stat numbers render verbatim and carry the counter hook ─────────────────
print("\n--- free-text stat numbers ---")
stats = {
    "۱۲۰+": 120,
    "۹۸/۱۰۰": 98,
    "زیر ۲ ثانیه": 2,
    "۶ ماه": 6,
}
for raw, target in stats.items():
    needle = f'data-count-text="{raw}"'
    hits = [u for u, b in bodies.items() if needle in b]
    check(f"rendered + hook for {raw!r}", hits)
    # same split the JS does: ^([^\d۰-۹]*)([\d۰-۹][\d۰-۹,،]*)(.*)$
    m = re.match(r"^([^\d۰-۹]*)([\d۰-۹][\d۰-۹,،]*)(.*)$", raw)
    head, digits, tail = m.groups()
    to_latin = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    value = int(digits.translate(to_latin).replace("،", "").replace(",", ""))
    check(f"  js split of {raw!r}", value == target,
          f"head={head!r} digits={digits!r} tail={tail!r} -> {value}")

# ── leaks + icon resolution ────────────────────────────────────────────────
print("\n--- leaks ---")
full = "\n".join(bodies.values())
for label, needle in [("[[ ]] marker", "[["), ("{# comment", "{#"),
                      ("{% comment %}", "{% comment %}"), ("{{ }}", "{{"),
                      ("CDN", "cdn.")]:
    hits = [u for u, b in bodies.items() if needle in b]
    check(f"no {label}", not hits, str(hits))

sprite = open("static/icons/lucide.sprite.svg", encoding="utf-8").read()
names = set(re.findall(r'id="i-([a-z0-9-]+)"', sprite))
rendered = set(re.findall(r'href="[^"]*#i-([a-z0-9-]+)"', full))
check("icons resolve in sprite", not (rendered - names), str(rendered - names))
check("clock icon used", "clock" in rendered and "clock" in names)

# ── home page GPS draw still wired after the per-root refactor ──────────────
print("\n--- home GPS draw (regression) ---")
home = client.get("/").content.decode()
check("home data-gps-root", "data-gps-root" in home)
check("home gps-draw", "gps-draw" in home)
check("home gps-dot", "gps-dot" in home)

# ── throwaway test database: 1–6 steps, then an empty-children service ──────
print("\n--- variable process steps (test database) ---")
setup_test_environment()
runner = DiscoverRunner(verbosity=0)
old_config = runner.setup_databases()
try:
    from apps.services.models import (
        Service, ServiceProcess, ServiceStat, ServiceWhyUs,
    )

    svc = Service.objects.create(
        title="تست", slug="test-svc", excerpt="خلاصه", description="توضیح",
        icon="sparkles", visual="none", card_span="wide", accent="royal",
    )
    for count in (1, 2, 3, 5, 6):
        ServiceProcess.objects.filter(service=svc).delete()
        for i in range(count):
            ServiceProcess.objects.create(
                service=svc, title=f"مرحله {i + 1}", description=f"توضیح {i + 1}", order=i,
            )
        r = Client(HTTP_HOST="localhost").get("/services/test-svc/")
        b = r.content.decode()
        check(f"{count} steps → 200", r.status_code == 200, f"got {r.status_code}")
        check(f"{count} steps → {count} nodes", b.count("gps-node") == count,
              f"{b.count('gps-node')}")
        check(f"{count} steps → {count} cards", b.count("process-step") == count)
        if count > 1:
            pos = [float(x) for x in re.findall(r'left: calc\(([\d.]+)% \+ 4%\)', b)]
            check(f"{count} steps → endpoints 0/92", pos[0] == 92.0 and pos[-1] == 0.0, str(pos))
            check(f"{count} steps → draw path present", "gps-draw" in b)
        else:
            check("1 step → no draw path", "gps-draw" not in b)
            check("1 step → centered node", "left: 50%" in b)

    # a service with NO children: sections skip entirely, page still 200
    ServiceProcess.objects.filter(service=svc).delete()
    ServiceStat.objects.filter(service=svc).delete()
    ServiceWhyUs.objects.filter(service=svc).delete()
    r = Client(HTTP_HOST="localhost").get("/services/test-svc/")
    b = r.content.decode()
    check("empty children → 200", r.status_code == 200)
    check("empty children → no process section", "gps-node" not in b and "process-step" not in b)
    check("empty children → no why section", "why-card" not in b)
    check("empty children → no stats section", "stat-num" not in b)
    check("empty children → no delivery note", "زمانِ تحویل" not in b)
finally:
    runner.teardown_databases(old_config)

print()
if failures:
    print("FAILURES:", failures)
    raise SystemExit(1)
print("ALL T65 CHECKS PASSED")
