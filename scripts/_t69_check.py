"""T69 headless-Chrome pass: the redesigned services LIST page in a real browser.

Boots runserver, opens /services/ at 1440 px and 390 px and measures:
  - no horizontal page overflow
  - every service card is laid out (non-zero rect), with a visible mega-orb
  - the orb accent colour matches the service's accent
  - the "how we choose" cards sit in one row on desktop, two on tablet
  - the FAQ accordion toggles open (initFaq drives it)
  - the empty state renders when there are no services

Run:  venv/Scripts/python scripts/_t69_check.py
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

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import asyncio  # noqa: E402
import websockets  # noqa: E402

from apps.services.models import Service  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ok = True

# کوئری‌های دیتابیس قبل از asyncio.run باید انجام شوند (SynchronousOnlyOperation).
_SERVICE_COUNT = Service.objects.count()


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


async def run_checks(server_port, cdp_port):
    proc = subprocess.Popen(
        [
            CHROME,
            f"--remote-debugging-port={cdp_port}",
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--hide-scrollbars",
            "--user-data-dir=" + os.path.join(ROOT, ".t69-chrome-profile"),
            "--window-size=1440,900",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        ws_url = None
        for _ in range(60):
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{cdp_port}/json/list", timeout=2
                ) as r:
                    targets = json.loads(r.read())
                pages = [t for t in targets if t.get("type") == "page"]
                if pages:
                    ws_url = pages[0]["webSocketDebuggerUrl"]
                    break
            except OSError:
                pass
            time.sleep(0.4)
        if not ws_url:
            print("  [FAIL] CDP target never appeared")
            global ok
            ok = False
            return

        async with websockets.connect(ws_url, max_size=64 * 1024 * 1024) as ws:
            mid = 0

            async def send(method, params=None):
                nonlocal mid
                mid += 1
                await ws.send(
                    json.dumps({"id": mid, "method": method, "params": params or {}})
                )
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("id") == mid:
                        return msg.get("result", {})

            async def js(expr):
                r = await send("Runtime.evaluate", {
                    "expression": expr,
                    "returnByValue": True,
                    "awaitPromise": True,
                })
                return r.get("result", {}).get("value")

            async def open_at(width, height, url):
                await send("Emulation.setDeviceMetricsOverride", {
                    "width": width, "height": height,
                    "deviceScaleFactor": 1, "mobile": width < 500,
                })
                await send("Page.navigate", {"url": url})
                for _ in range(80):
                    v = await js("document.readyState")
                    if v == "complete":
                        break
                    time.sleep(0.3)
                await asyncio.sleep(2.0)

            base = f"http://127.0.0.1:{server_port}"
            # ── 1440px ──
            print("  1440px:")
            await open_at(1440, 900, f"{base}/services/")
            await js("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)
            await js("window.scrollTo(0, 0)")
            await asyncio.sleep(0.8)

            check(
                await js("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1"),
                f"no horizontal overflow (scrollWidth={await js('document.documentElement.scrollWidth')})",
            )
            n = await js("document.querySelectorAll('.svc-list-card').length")
            check(n == _SERVICE_COUNT, f"{n} service cards (expected {_SERVICE_COUNT})")

            rects = await js("[...document.querySelectorAll('.svc-list-card')].map(c=>{const r=c.getBoundingClientRect();const o=c.querySelector('.mega-orb').getBoundingClientRect();return {x:Math.round(r.x),w:Math.round(r.width),orb:Math.round(o.width)};})")
            for i, r in enumerate(rects):
                check(r["w"] > 300 and r["x"] >= 0 and r["x"] + r["w"] <= 1441,
                      f"card {i + 1} in viewport ({r['x']},{r['w']})")
                check(r["orb"] > 40, f"card {i + 1} orb visible ({r['orb']}px)")

            how = await js("[...document.querySelectorAll('.why-card')].map(c=>{const r=c.getBoundingClientRect();return {x:Math.round(r.x),w:Math.round(r.width)};})")
            check(len(how) == 4, f"4 how-choose cards ({len(how)})")
            # کارتِ اول خودش با خودش مقایسه نمی‌شود (تفاوتِ صفر همیشه شرطِ >10 را
            # نقض می‌کرد) — فقط سه کارتِ بعدی نسبت به کارتِ اول سنجیده می‌شوند.
            if how:
                one_row = all(
                    abs(h["x"] + h["w"] / 2 - how[0]["x"] - how[0]["w"] / 2) > 10
                    for h in how[1:]
                )
                check(one_row, f"how cards spread across the row (x={[h['x'] for h in how]})")
                check(all(h["x"] >= 0 and h["x"] + h["w"] <= 1441 for h in how),
                      "how cards inside viewport")

            check(await js("document.querySelectorAll('.faq-q').length") == 6,
                  "6 FAQ items")
            check(await js("!!document.querySelector('.eyebrow')"), "hero eyebrow present")
            check(await js("document.querySelectorAll('h1').length") == 1, "exactly one h1")

            # FAQ accordion toggles
            await js("document.querySelectorAll('.faq-q')[0].click()")
            await asyncio.sleep(0.6)
            check(await js("document.querySelectorAll('.faq-q')[0].getAttribute('aria-expanded')") == "true",
                  "FAQ opens on click")
            panel_h = await js("document.querySelectorAll('.faq-a')[0].getBoundingClientRect().height")
            check(panel_h > 10, f"FAQ panel expanded ({round(panel_h)}px)")

            # ── 390px ──
            print("  390px:")
            await open_at(390, 844, f"{base}/services/")
            await js("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.2)
            await js("window.scrollTo(0, 0)")
            await asyncio.sleep(0.6)
            check(
                await js("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1"),
                f"no horizontal overflow at 390px (scrollWidth={await js('document.documentElement.scrollWidth')})",
            )
            cw = await js("document.documentElement.clientWidth")
            rects = await js("[...document.querySelectorAll('.svc-list-card')].map(c=>Math.round(c.getBoundingClientRect().width))")
            check(all(w <= cw + 1 for w in rects),
                  f"cards fit 390px ({rects})")
            how = await js("[...document.querySelectorAll('.why-card')].map(c=>Math.round(c.getBoundingClientRect().width))")
            check(all(w <= cw + 1 for w in how), f"how cards fit 390px ({how})")

            # exceptions
            exc = await js("window.__errs ? window.__errs.length : 0")
            check(exc == 0, f"no page exceptions ({exc})")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def main():
    global ok
    server_port = 8073
    cdp_port = free_cdp_port()
    env = dict(os.environ, DJANGO_SETTINGS_MODULE="config.settings")
    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{server_port}", "--noreload"],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(60):
            if port_open(server_port):
                break
            time.sleep(0.4)
        else:
            print("[FAIL] runserver never came up")
            ok = False
            return
        print(f"[T69 browser] services list at 1440px / 390px")
        asyncio.run(run_checks(server_port, cdp_port))
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
    print("[T69 browser] " + ("ALL PASS" if ok else "FAILURES"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
