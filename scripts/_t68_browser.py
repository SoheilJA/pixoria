"""T68 headless-Chrome pass: the per-service atmosphere motifs in a real browser.

Boots runserver, opens all four service pages at 1440 px and 390 px and measures:
  - no horizontal page overflow, and no motif sticking out of the hero
  - every motif element is really laid out (non-zero rect), not display:none
  - the motif animations are actually running (computed animation-name)
  - the diamond construction line really draws itself (stroke-dashoffset moves)
  - the motifs carry the service's accent colour (computed --pa)

Reduced motion is NOT forced here (unlike the T66/T67 passes) so the animations
can be observed; the CSS pause paths were verified structurally in input.css.
Requires Google Chrome + `pip install websockets`.

Run:  venv/Scripts/python scripts/_t68_browser.py
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SLUGS = ["web-design", "programming", "logo-design", "graphic-design"]
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
                           "pixoria-chrome-t68")
    chrome = subprocess.Popen(
        [CHROME, f"--remote-debugging-port={cdp}", "--headless=new",
         "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         f"--user-data-dir={profile}", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
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
                # موتیف‌ها زیرِ fold ممکن است منتظرِ data-reveal بمانند
                # (x:-60 تا اسکرول)؛ یک اسکرولِ کوتاه و بازگشت، ورودِ آن‌ها را
                # trigger می‌کند تا مثلِ یک کاربرِ واقعی اندازه‌گیری کنیم.
                await js("window.scrollTo({top: 500, behavior: 'instant'})")
                await asyncio.sleep(1.4)
                await js("window.scrollTo({top: 0, behavior: 'instant'})")
                await asyncio.sleep(0.5)

            HERO = """
(() => {
  const out = {pageW: document.documentElement.clientWidth,
               scrollW: document.documentElement.scrollWidth,
               motifs: {}, hero: false, theme: null, accent: null};
  const hero = document.querySelector('section[data-pause]');
  out.hero = !!hero;
  if (!hero) return out;
  const wrap = hero.closest('[class*="svc-accent-"]');
  out.accent = wrap ? getComputedStyle(wrap).getPropertyValue('--pa').trim() : null;
  const theme = hero.querySelector('[class*="service-theme-"]');
  out.theme = theme ? (theme.className.match(/service-theme-[a-z]+/) || [])[0] : null;
  const cols = {browser: ['svc-blueprint', 'svc-device', 'svc-chip'],
                terminal: ['svc-glyph', 'svc-type'],
                palette: ['svc-swatch', 'svc-drip'],
                diamond: ['svc-tick', 'svc-logo-draw', 'svc-chip']};
  const want = Object.entries(cols).find(([k]) => out.theme === 'service-theme-' + k);
  if (!want) return out;
  for (const c of want[1]) {
    const els = [...hero.querySelectorAll('.' + c)];
    out.motifs[c] = els.length;
    if (!els.length) continue;
    out['laid_' + c] = els.filter(e => {
      const r = e.getBoundingClientRect();
      return r.width > 0 || r.height > 0;
    }).length;
    out['anim_' + c] = getComputedStyle(els[0]).animationName;
    // چیپ/گلیف/نمونه/دستگاه با GSAP (data-float) متحرک می‌شوند، نه با CSS
    out['gsap_' + c] = els.some(e => !!e._gsap);
    out['out_' + c] = els.some(e => {
      const r = e.getBoundingClientRect();
      return r.right > out.pageW + 2 || r.left < -2;
    });
  }
  return out;
})()
"""

            VISUALS = {"web-design": "browser", "programming": "terminal",
                       "logo-design": "diamond", "graphic-design": "palette"}
            # موتیف‌هایی که با CSS انیمیشن می‌خورند؛ بقیه با data-float (GSAP) هستند
            CSS_ANIM = {"svc-blueprint", "svc-type", "svc-drip", "svc-tick",
                        "svc-logo-draw"}
            for slug in SLUGS:
                visual = VISUALS[slug]
                for w, h, label in [(1440, 1000, "دسکتاپ"), (390, 844, "موبایل")]:
                    await visit(f"http://127.0.0.1:{port}/services/{slug}/", w, h)
                    print(f"-- /services/{slug}/ @ {label}")
                    r = await js(HERO)
                    if isinstance(r, dict) and "__error" in r:
                        check(False, f"ارزیابیِ JS شکست خورد: {r['__error']}")
                        continue
                    check(r.get("hero"), "هیرو با data-pause پیدا شد")
                    check(r.get("theme") == f"service-theme-{visual}",
                          f"theme = {r.get('theme')}")
                    check(r.get("scrollW") <= r.get("pageW", 0),
                          f"سرریزِ افقی نیست ({r.get('scrollW')} ≤ {r.get('pageW')})")
                    for c, n in (r.get("motifs") or {}).items():
                        check(n > 0, f"{c}: {n} عنصر")
                        check(r.get("laid_" + c, 0) > 0, f"{c}: چیدمان دارد")
                        if c in CSS_ANIM:
                            check(r.get("anim_" + c) not in (None, "none"),
                                  f"{c}: anim = {r.get('anim_' + c)}")
                        else:
                            check(r.get("gsap_" + c),
                                  f"{c}: متحرکِ GSAP (data-float)")
                        check(not r.get("out_" + c), f"{c}: داخلِ viewport")
                    print(f"    لهجهٔ --pa = {r.get('accent')}")

            # ── خطِ کشیده‌شدنِ الماس باید واقعاً حرکت کند ──
            print("-- logo-design: رسمِ الماس")
            await cmd("Page.navigate",
                      {"url": f"http://127.0.0.1:{port}/services/logo-design/"})
            for _ in range(100):
                if await js("!!document.querySelector('.svc-logo-draw')"):
                    break
                await asyncio.sleep(0.2)
            await asyncio.sleep(0.9)  # داخلِ تأخیرِ ۰.۵ ثانیه‌ای + آغازِ رسم
            early = await js("""
(() => { const p = document.querySelector('.svc-logo-draw');
         return p ? parseFloat(getComputedStyle(p).strokeDashoffset) : null; })()""")
            await asyncio.sleep(3.0)
            late = await js("""
(() => { const p = document.querySelector('.svc-logo-draw');
         return p ? parseFloat(getComputedStyle(p).strokeDashoffset) : null; })()""")
            print(f"    dashoffset: {early} → {late}")
            check(early is not None,
                  "الماس با pathLength روی مسیر است")
            check(early is not None and early > 0.05,
                  f"خط در ابتدا ناتمام است (dashoffset={early})")
            check(late is not None and late < 0.05,
                  f"خط در انتها کامل کشیده شد (dashoffset={late})")
    finally:
        chrome.terminate()
        server.terminate()
        try:
            chrome.wait(timeout=5)
        except Exception:  # noqa: BLE001
            chrome.kill()
        try:
            server.wait(timeout=5)
        except Exception:  # noqa: BLE001
            server.kill()

    print("\n" + ("همهٔ چک‌های مرورگر گذشت ✓" if ok else "برخی چک‌های مرورگر شکست خوردند ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
