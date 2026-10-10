"""T67 headless-Chrome pass: the new social-proof / discovery sections on the
service detail page — testimonials slider, related-projects carousel and
related-articles carousel — measured in a real browser at 1440 px and 390 px.

The live DB has no projects/articles tied to a service, so the script links the
existing rows to web-design for the duration of the run and REVERTS them in a
finally (the DB is git-tracked too, so `git checkout -- database/db.sqlite3` is
a second safety net). Requires Google Chrome + `pip install websockets`.

Run:  venv/Scripts/python scripts/_t67_browser.py
"""
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request

# پروکسیِ محلیِ سیستم روی 127.0.0.1 دخالت می‌کند؛ CDP و runserver مستقیم هستند.
for _v in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY"):
    os.environ.pop(_v, None)
os.environ["NO_PROXY"] = "127.0.0.1,localhost"
os.environ["no_proxy"] = "127.0.0.1,localhost"

import django  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import asyncio  # noqa: E402
import websockets  # noqa: E402

from apps.portfolio.models import Portfolio  # noqa: E402
from apps.blog.models import Article  # noqa: E402
from apps.services.models import ServiceTestimonial  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SLUG = "web-design"
ok = True


def check(cond, label):
    global ok
    if not cond:
        ok = False
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def port_open(port):
    s = socket.socket()
    s.settimeout(0.3)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def free_cdp_port():
    for _ in range(20):
        port = free_port()
        if not port_open(port):
            return port
    return free_port()


# ── دادهٔ موقت: پروژه‌ها و مقالات را به web-design وصل می‌کنیم ──────────
# (در finally دقیقاً برمی‌گردند؛ دیتابیس هم در git هست).
from apps.services.models import Service  # noqa: E402

_service = Service.objects.get(slug=SLUG)
projects = list(Portfolio.objects.all())
articles = list(Article.objects.filter(status="published"))
proj_before = {p.pk: p.service_id for p in projects}
art_before = {a.pk: list(a.related_services.values_list("pk", flat=True)) for a in articles}
for p in projects:
    p.service = _service
    p.save(update_fields=["service"])
for a in articles[:2]:
    a.related_services.add(_service.pk)
# از سه نظرِ web-design فقط یکی playable است (دو رسانه‌ای فایل/آدرس ندارند —
# D54 کارتِ پلیرِ شکسته چاپ نمی‌کند)؛ این عدد برای assertionِ پایین لازم است.
PLAYABLE = ServiceTestimonial.objects.filter(
    service=_service,
    kind="text", text__gt="").count()
print(f"linked {len(projects)} projects and 2 articles to {SLUG} temporarily "
      f"({PLAYABLE} playable testimonial)")

async def main():
    global ok
    port = free_port()
    cdp = free_cdp_port()
    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}",
         "--noreload", "--nothreading"],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    profile = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")),
                           "pixoria-chrome-t67")
    chrome = subprocess.Popen(
        [CHROME, f"--remote-debugging-port={cdp}", "--headless=new",
         "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         "--force-prefers-reduced-motion",
         f"--user-data-dir={profile}", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        no_proxy = urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(no_proxy)
        for _ in range(120):
            try:
                opener.open(f"http://127.0.0.1:{port}/", timeout=1)
                break
            except Exception:
                time.sleep(0.5)
        targets, last_err = None, None
        for _ in range(90):
            try:
                with opener.open(f"http://127.0.0.1:{cdp}/json/list", timeout=1) as r:
                    targets = json.load(r)
                if [t for t in targets if t.get("type") == "page"]:
                    break
            except Exception as exc:  # noqa: BLE001
                last_err, targets = exc, None
            time.sleep(0.5)
        if not targets:
            raise RuntimeError(f"CDP never came up on :{cdp} ({last_err})")
        page = [t for t in targets if t.get("type") == "page"][0]

        async with websockets.connect(page["webSocketDebuggerUrl"]) as ws:
            mid = [0]

            async def cmd(method, params=None):
                mid[0] += 1
                await ws.send(json.dumps({"id": mid[0], "method": method,
                                          "params": params or {}}))
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("id") == mid[0]:
                        return msg.get("result", {})

            async def js(expr):
                r = await cmd("Runtime.evaluate", {
                    "expression": expr, "returnByValue": True,
                    "awaitPromise": True})
                if r and "exceptionDetails" in r:
                    return {"__error": r["exceptionDetails"].get("text", "js error")}
                return r.get("result", {}).get("value")

            async def visit(url, w, h):
                await cmd("Emulation.setDeviceMetricsOverride",
                          {"width": w, "height": h, "deviceScaleFactor": 1,
                           "mobile": w < 700})
                await cmd("Page.navigate", {"url": url})
                for _ in range(100):
                    if await js("document.readyState === 'complete'"):
                        break
                    await asyncio.sleep(0.2)
                await asyncio.sleep(1.2)

            # ── دسکتاپ ──
            await visit(f"http://127.0.0.1:{port}/services/{SLUG}/", 1440, 1000)
            print(f"-- {SLUG} @1440")
            r = await js("""
(() => {
  const out = {pageW: document.documentElement.clientWidth,
               scrollW: document.documentElement.scrollWidth};
  const find = (needle) => [...document.querySelectorAll('h2')]
      .find(h => h.textContent.includes(needle));
  const secProject = find('کارهایی که با');
  const secArticle = find('بیشتر دربارهٔ');
  out.projects = !!secProject;
  out.articles = !!secArticle;
  for (const [key, sec] of [['proj', secProject], ['art', secArticle]]) {
    if (!sec) continue;
    const root = sec.closest('section');
    const track = root.querySelector('[data-carousel-track]');
    out[key + 'Cards'] = track ? track.children.length : 0;
    const cards = track ? [...track.children] : [];
    out[key + 'Widths'] = cards.map(c => Math.round(c.getBoundingClientRect().width));
    out[key + 'Cols'] = new Set(cards.map(c => Math.round(c.getBoundingClientRect().top))).size;
    out[key + 'Scroll'] = track ? track.scrollWidth : 0;
    out[key + 'Client'] = track ? track.clientWidth : 0;
    // کارت‌ها باید سرِ ردیف بیرون از viewport نباشند
    out[key + 'Overflow'] = cards.some(c => c.getBoundingClientRect().right > out.pageW + 2);
    out[key + 'Link'] = !!root.querySelector('.more-link-light');
  }
  // اسلایدرِ نظرات
  const slider = document.querySelector('[data-slider-root]');
  out.slider = !!slider;
  out.sliderCards = slider ? slider.querySelectorAll('[data-slider] > *').length : 0;
  // آکاردئون
  out.faq = document.querySelectorAll('.faq-q').length;
  // خدماتِ مرتبط
  const rel = [...document.querySelectorAll('h2')]
      .find(h => h.textContent.includes('یکجا'));
  out.related = rel ? rel.closest('section').querySelectorAll('a[href*="/services/"]').length : 0;
  // JSON-LD
  const ld = document.querySelector('script[type="application/ld+json"]');
  if (ld) {
    const g = JSON.parse(ld.textContent);
    const types = g['@graph'].map(n => n['@type']);
    out.ldTypes = types;
    out.offers = g['@graph'].find(n => n['@type'] === 'Service').offers?.length || 0;
  }
  return out;
})()
            """)
            if isinstance(r, dict) and r.get("__error"):
                check(False, f"JS error: {r['__error']}")
            else:
                check(r and r.get("projects"), "projects section rendered")
                check(r and r.get("projCards", 0) == 2, f"2 project cards (got {r and r.get('projCards')})")
                # کاروسل همیشه یک ردیف است (scroll-snap افقی)؛ «ستون» برای
                # گریدِ قیمت‌گذاری معنا داشت، نه اینجا.
                check(r and r.get("projCols", 0) == 1, f"carousel is one row ({r and r.get('projCols')})")
                check(r and len(set(r.get("projWidths", []))) == 1, "project cards equal width")
                check(r and not r.get("projOverflow"), "no card past the right edge")
                check(r and r.get("projLink"), "projects more-link-light present")
                check(r and r.get("articles"), "articles section rendered")
                check(r and r.get("artCards", 0) == 2, f"2 article cards (got {r and r.get('artCards')})")
                check(r and r.get("artLink"), "articles more-link-light present")
                # فقط نظراتِ playable چاپ می‌شوند (دو رسانه‌ای فایل ندارند، D54)
                check(r and r.get("sliderCards", 0) == PLAYABLE,
                      f"{PLAYABLE} playable testimonial card (got {r and r.get('sliderCards')})")
                check(r and r.get("faq", 0) == 8, f"8 faq items (got {r and r.get('faq')})")
                check(r and r.get("related", 0) == 3, f"3 related-service cards (got {r and r.get('related')})")
                check(r and sorted(r.get("ldTypes", [])) == ["BreadcrumbList", "FAQPage", "Service"],
                      f"JSON-LD graph {r and r.get('ldTypes')}")
                check(r and r.get("offers") == 3, f"3 offers ({r and r.get('offers')})")
                check(r and r.get("scrollW", 999) <= r.get("pageW", 0) + 1,
                      f"no page h-overflow ({r and r.get('scrollW')} > {r and r.get('pageW')})")
                print(f"     project card widths: {r.get('projWidths')} | article widths: {r.get('artWidths')}")

            # ── موبایل ──
            await visit(f"http://127.0.0.1:{port}/services/{SLUG}/", 390, 900)
            print(f"-- {SLUG} @390")
            r = await js("""
(() => {
  const find = (needle) => [...document.querySelectorAll('h2')]
      .find(h => h.textContent.includes(needle));
  const out = {pageW: document.documentElement.clientWidth,
               scrollW: document.documentElement.scrollWidth};
  for (const [key, sec] of [['proj', find('کارهایی که با')], ['art', find('بیشتر دربارهٔ')]]) {
    if (!sec) { out[key] = false; continue; }
    const track = sec.closest('section').querySelector('[data-carousel-track]');
    const cards = track ? [...track.children] : [];
    out[key] = true;
    out[key + 'Cards'] = cards.length;
    out[key + 'Widths'] = cards.map(c => Math.round(c.getBoundingClientRect().width));
    out[key + 'Overflow'] = cards.some(c => c.getBoundingClientRect().right > out.pageW + 2);
  }
  return out;
})()
            """)
            check(r and r.get("proj"), "mobile projects section rendered")
            check(r and r.get("projCards", 0) == 2, f"2 project cards at 390")
            widths = r and r.get("projWidths") or []
            check(bool(widths) and max(widths) <= r.get("pageW", 0) + 2,
                  f"project cards fit 390 ({widths})")
            check(r and not r.get("projOverflow"), "no card past the right edge at 390")
            check(r and r.get("art"), "mobile articles section rendered")
            check(r and r.get("scrollW", 999) <= r.get("pageW", 0) + 1,
                  f"no page h-overflow at 390 ({r and r.get('scrollW')} > {r and r.get('pageW')})")
    finally:
        chrome.terminate()
        server.terminate()
        for proc in (chrome, server):
            try:
                proc.wait(timeout=5)
            except Exception:
                pass

    print("\nRESULT:", "ALL PASS" if ok else "FAILURES PRESENT")


try:
    asyncio.run(main())
finally:
    # ── برگرداندنِ دادهٔ موقت (همیشه، حتی در صورتِ خطا) ──
    for pk, svc in proj_before.items():
        Portfolio.objects.filter(pk=pk).update(service=svc)
    for a in Article.objects.filter(pk__in=art_before):
        a.related_services.set(art_before[a.pk])
    print("reverted temporary project/article links")
    print(f"projects still linked to {SLUG}: "
          f"{Portfolio.objects.filter(service=_service).count()} (expect 0)")

sys.exit(0 if ok else 1)
