"""T66 headless-Chrome pass: start the dev server, open each service page and
the prefill contact link, and measure the rendered geometry of the pricing
section (card columns, badge position, calculator total, no horizontal
overflow). Requires Google Chrome; installs nothing else.

Run:  venv/Scripts/python scripts/_t66_browser.py
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

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import asyncio  # noqa: E402
import websockets  # noqa: E402

from apps.services.models import Service  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ok = True

# کوئریِ DB باید خارج ازِ حلقهٔ async باشد (Django اجازه نمی‌دهد).
SERVICES = [s.slug for s in Service.objects.all()]


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
    """یک پورتِ آزاد برای دیباگِ کروم — پورت‌های درگیرِ احتمالی را رها می‌کند."""
    for _ in range(20):
        port = free_port()
        if not port_open(port):
            return port
    return free_port()


async def main():
    port = free_port()
    cdp = free_cdp_port()
    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}",
         "--noreload", "--nothreading"],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    profile = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")),
                           "pixoria-chrome-t66")
    chrome = subprocess.Popen(
        [CHROME, f"--remote-debugging-port={cdp}", "--headless=new",
         "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         "--force-prefers-reduced-motion",
         f"--user-data-dir={profile}", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        # صبر تا هر دو سرور بالا بیایند.
        no_proxy = urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(no_proxy)
        for _ in range(120):
            try:
                opener.open(f"http://127.0.0.1:{port}/", timeout=1)
                break
            except Exception:
                time.sleep(0.5)
        targets = None
        last_err = None
        # پروکسیِ محلیِ احتمالی را دور می‌زنیم — CDP روی 127.0.0.1 مستقیم است.
        no_proxy = urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(no_proxy)
        for _ in range(90):
            try:
                with opener.open(
                        f"http://127.0.0.1:{cdp}/json/list", timeout=1) as r:
                    targets = json.load(r)
                pages = [t for t in targets if t.get("type") == "page"]
                if pages:
                    break
            except Exception as exc:  # noqa: BLE001 — دوباره تلاش می‌کنیم
                last_err = exc
                targets = None
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
                return r.get("result", {}).get("value")

            async def visit(url, w, h):
                await cmd("Emulation.setDeviceMetricsOverride",
                          {"width": w, "height": h, "deviceScaleFactor": 1,
                           "mobile": w < 700})
                await cmd("Page.navigate", {"url": url})
                for _ in range(100):
                    v = await js("document.readyState === 'complete'")
                    if v:
                        break
                    await asyncio.sleep(0.2)
                await asyncio.sleep(1.0)

            services = SERVICES
            for s in services:
                await visit(f"http://127.0.0.1:{port}/services/{s}/",
                            1440, 1000)
                print(f"-- {s} @1440")
                r = await js("""
(() => {
  const out = {};
  const sec = [...document.querySelectorAll('h2')]
      .find(h => h.textContent.includes('تعرفه'));
  out.hasPricing = !!sec;
  if (!sec) return out;
  // section ⊃ div.container ⊃ h2؛ کارت‌ها را خودِ section می‌گیریم.
  const root = sec.closest('section');
  const cards = [...root.querySelectorAll('article')];
  out.cards = cards.length;
  out.sectionTag = root.tagName;
  const xs = cards.map(c => c.getBoundingClientRect().left);
  const xe = cards.map(c => c.getBoundingClientRect().right);
  // پلنِ پیشنهادی با md:-mt-6 بالا‌تر می‌نشیند؛ ستون‌ها را با left می‌سنجیم.
  out.cardCols = new Set(cards.map(c => Math.round(c.getBoundingClientRect().left))).size;
  out.cardTops = cards.map(c => Math.round(c.getBoundingClientRect().top));
  out.cardWidths = cards.map(c => Math.round(c.getBoundingClientRect().width));
  out.sameRow = Math.max(...xe) - Math.min(...xs);
  out.pageW = document.documentElement.clientWidth;
  out.scrollW = document.documentElement.scrollWidth;
  // اگر پلنِ وسط featured باشد، کارت ۶rem بالاتر است؛ برچسب باید بالایِ
  // همان کارت باشد، نه لزوماً بالایِ صفرِ صفحه.
  const badge = root.querySelector('span[style*="linear-gradient"]');
  if (badge) {
    const card = badge.closest('article');
    out.badgeTop = Math.round(badge.getBoundingClientRect().top);
    out.cardTop = Math.round(card.getBoundingClientRect().top);
  } else {
    out.badgeTop = null;
  }
  // ماشین‌حساب (یک div جدا از کارت‌ها، داخلِ همان section)
  const calc = root.querySelector('[data-custom-root]');
  out.custom = !!calc;
  if (calc) {
    const total = calc.querySelector('[data-custom-total]');
    out.total0 = total ? total.textContent : null;
    const box = calc.querySelector('[data-custom-price]');
    box.checked = true;
    box.dispatchEvent(new Event('change', {bubbles: true}));
    out.totalChecked = total ? total.textContent : null;
    box.checked = false;
    box.dispatchEvent(new Event('change', {bubbles: true}));
  }
  // اولین قیمتِ رندرشده
  const price = root.querySelector('.fa-num');
  out.firstPrice = price ? price.textContent : null;
  return out;
})()
                """)
                check(r and r.get("hasPricing"), "pricing section rendered")
                check(r and r.get("cards", 0) == 3, f"3 plan cards (got {r and r.get('cards')})")
                check(r and r.get("cardCols", 0) == 3,
                      f"cards side by side at 1440 (got {r and r.get('cardCols')})")
                tops = r and r.get("cardTops") or []
                # کارتِ وسط (featured) باید بالاتر از دو تای دیگر باشد.
                check(bool(tops) and tops[1] < tops[0] and tops[1] < tops[2],
                      f"featured card elevated ({tops})")
                check(r and r.get("scrollW", 999) <= r.get("pageW", 0) + 1,
                      f"no h-overflow ({r and r.get('scrollW')} > {r and r.get('pageW')})")
                if r and r.get("custom"):
                    check(r["total0"] == "۰", f"calculator starts at ۰ (got {r['total0']})")
                    check(r["totalChecked"] != "۰" and r["totalChecked"] is not None,
                          f"calculator sums ({r['totalChecked']})")
                    check(r["totalChecked"] == r.get("_reset", r["totalChecked"]), "")
                if r and r.get("badgeTop") is not None:
                    check(r["badgeTop"] < r.get("cardTop", 0),
                          f"badge above its card ({r['badgeTop']} < {r.get('cardTop')})")
                print(f"     prices/cards: {r and r.get('firstPrice')} | "
                      f"{r and r.get('cardWidths')}")

            # موبایل
            s0 = services[0]
            await visit(f"http://127.0.0.1:{port}/services/{s0}/", 390, 900)
            print(f"-- {s0} @390")
            r = await js("""
(() => {
  const sec = [...document.querySelectorAll('h2')].find(h => h.textContent.includes('تعرفه'));
  if (!sec) return {hasPricing: false};
  const cards = [...sec.closest('section').querySelectorAll('article')];
  return {
    hasPricing: true,
    cards: cards.length,
    cols: new Set(cards.map(c => Math.round(c.getBoundingClientRect().left))).size,
    cardWidths: cards.map(c => Math.round(c.getBoundingClientRect().width)),
    pageW: document.documentElement.clientWidth,
    scrollW: document.documentElement.scrollWidth,
  };
})()
            """)
            check(r and r.get("hasPricing"), "mobile pricing rendered")
            check(r and r.get("cards", 0) == 3, f"3 cards on mobile")
            widths = r and r.get("cardWidths")
            check(bool(widths) and max(widths) <= r.get("pageW", 0) + 1,
                  f"card widths fit viewport at 390 ({widths})")
            check(r and r.get("scrollW", 999) <= r.get("pageW", 0) + 1,
                  f"no h-overflow at 390 ({r and r.get('scrollW')} > {r and r.get('pageW')})")

            # لینکِ prefill
            await visit(f"http://127.0.0.1:{port}/contact/?plan=pro&service=web-design",
                        1440, 1000)
            print("-- prefill contact link")
            r = await js("""
(() => {
  const sel = document.querySelector('select[name=subject]');
  const note = document.querySelector('.lg\\\\:col-span-8 strong');
  const msg = document.querySelector('textarea[name=message]');
  return {
    subject: sel ? sel.value : null,
    note: note ? note.textContent : null,
    message: msg ? msg.value : null,
    errors: !!document.querySelector('.field-err'),
  };
})()
            """)
            check(r and r["subject"] == "درخواست سفارش پروژه",
                  f"subject prefilled ({r and r['subject']})")
            check(r and r["note"] and "خدمتِ" in r["note"] and "پلنِ" in r["note"],
                  f"note shown ({r and r['note']})")
            check(r and r["message"] and "پلن" in r["message"],
                  f"message prefilled ({r and r['message']})")
            check(r and not r["errors"], "no validation errors on GET")
    finally:
        chrome.terminate()
        server.terminate()
        try:
            chrome.wait(timeout=5)
        except Exception:
            pass
        try:
            server.wait(timeout=5)
        except Exception:
            pass

    print("\nRESULT:", "ALL PASS" if ok else "FAILURES PRESENT")


asyncio.run(main())
sys.exit(0 if ok else 1)
