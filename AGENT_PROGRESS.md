
### دنبالهٔ ۳۲ — وندورِ لوکالِ @lucasmarkes/hairline (v0.5.1، MIT)
- درخواستِ کاربر با فایلِ `hairline.txt` در روت: کتابخانهٔ `@lucasmarkes/hairline` کشف شد (۳۳ فیگورِ خطیِ ایزومتریکِ pointer-reactive: riffle/terrain/vault/terminal/turntable/…، خروجی SVG با نسبت ۵:۴، API فانکشنی `fig(el,{play:true})` + `update`/`destroy` — شبیه Svelte action.
- از رجیستری npm تاربال رسمی (v0.5.1) دانلود و `dist/index.js` (مینیفای، Pure ESM، **هیچ** import و وابستگی — react فقط peerِ اختیاریِ wrapper جدا) برداشته شد به `static/js/vendor/hairline.js` با بنرِ نسخه/لایسنس؛ خطِ `sourceMappingURL` حذف شد (map وندور نشد، ری‌اکت wrapper به دلیل vanilla بودنِ پروژه نیامد).
- `collectstatic` → هشِ `js/vendor/hairline.d2a5f17f7102.js`. پروبِ مرورگر روی `/about/`: import ماژولِ ۳۳ خروجی، رندرِ `riffle` در ۳ دایو (SVG 280×224)، `update({intensity})` و `destroy()` تمیز — سبز. یک گیر: cache ۴۰۴ِ مرورگر بعد از ری‌استارتِ سرور — با `?v=2` دور زده شد (نه مشکلِ پکیج، نه مشکلِ سرور).
- استفادهٔ عملی در قالب بعداً: `<script type="module" src="{% static %}">` یا `import()` داینامیک از `pixoria.js`. فایل `hairline.txt` روت مستقل ماند (کامیت نشد).

### دنبالهٔ ۳۳ — فیگورهای @hairline در سه ناحیهٔ سایت
- **لودر:** `static/js/hairline-figs.js` (module، `data-hl-lib` از `{% static %}` در base.html) — مونتِ اعلامی روی `[data-hl]` با `data-hl-intensity`، import یکبارِ وندورِ `vendor/hairline.js`، سکنِ دوباره در `htmx:afterSettle` (hx-boost کلِ body سواپ میکند)، خنثی در `prefers-reduced-motion`، کلاسِ `hl-broken` (بافتِ dashed) برای شکستِ شبکه، و re-mount با debounce در resize چون کتابخانه ResizeObserver ندارد (svg فقط در لحظهٔ مونت اندازه میگیرد).
- **چرا پیکسوریا (why):** پینهای ثابتِ `why-chip__pins` و علامتِ `PIX·NN` حذف؛ هر ماژول حالا پنلِ تیرهٔ کوچک با فیگورِ خودش دارد: `{% cycle 'terminal' 'keyboard' 'plot' 'hub' 'turntable' 'vault' %}` (intensity 0.55) + هاورِ طلایی. CSSهای مرده پاک شد.
- **مهارتها (tech):** کنار نوارهای مارکوی، پنلِ `tech-fig` با فیگورِ `plot` (نمودارِ میلهها — intensity 0.7). گریدِ دوستونه به‌صورت دستسازِ `.tech-grid` در sections.css — نکته: کلاسِ arbitrary جدید (`grid-cols-[minmax(0,1fr)]`) بدونِ بیلدِ tailwind وجود ندارد و پنل تا ۲۰۲۷px باز میشد؛ با rail دستی حل شد.
- **CTA (فینال):** پنلِ `cta-fig` تیره با فیگورِ `vault` (intensity 0.65) بعد از توضیحات و قبل از دکمهها؛ mx-auto، تا 20.5rem، هالهٔ طلایی.
- **CSS مشترک:** `aspect-ratio: 5/4` روی همهٔ میزبانها تا مونتِ SVG بدونِ CLS.
- **پروب زنده:** ۸ فیگور مونت (۶×why در ۳۷۲×۲۹۷، plot در ۹۷۷×۷۸۱، vault در ۳۲۶×۲۶۰) — همه دقیقاً ۵:۴، بدونِ overflow. `manage.py check` سبز؛ collectstatic + restart.
- فایلِ `hairline.txt` روت دست‌نخورده ماند (یادداشتِ شخصی کاربر؛ کامیت نشد).

## دنبالهٔ ۳۴ — ری‌دی‌زاینِ کاملِ سکشن «چرا پیکسوریا» (سه‌شنبه ۲۹ مهر ۱۴۰۵)

- **هدف:** کاربر خواست سکشن «۶ دلیل» کلاً ری‌دی‌زاین شود؛ موبایل‌فرست و با UI جذاب.
- **طرحِ جدید v4 «آلبومِ استودیو»** (`03cec43`):
  - **موبایل (base):** ریلِ اسنپِ افقی (workaround اسکرولِ بدونِ اسکرول‌بار) با کارتِ ~79vw، لبه‌های محوِ کرمی، نشانگرِ «برای دیدنِ بقیه بکشید» (فقط موبایل، `display:none` از sm به بعد)؛ snap مرکزی + `overscroll-behavior-inline: contain`.
  - **≥640px:** گریدِ ۲ستونه؛ اسنپ خاموش؛ لبه‌های محو و نشانگر حذف.
  - **≥1024px:** بنتوی ۴ستونه؛ **کارتِ ۱ و ۶ پهنِ دونیمه** با لایه‌بندیِ دونیمه (تیتر/متن سمتِ راست، فیگورِ sمتِ چپِ کارت)، `width: min(100%, 300px)` برای فیگور تا ارتفاعِ کارتِ ردیف کنترل بماند.
  - **کارت:** شمارهٔ شبحوارهٔ طلایی (۰۱..۰۶ با `fa_digits` + `-webkit-text-stroke`، فالبکِ رنگِ شفاف بدونِ stroke)، آیکن‌رینگ، فیگورِ خطیِ زندهٔ hairline روی تِختهٔ تیره (data-hl cycle همان ۶ فیگور، intensity 0.55)، خطِ «درزِ طلایی» دست‌ساز که در هاور از ۲۵٪ به ۱۰۰٪ کشیده میشود (`transform-origin: 100% 50%` برای RTL)، هاور: بالا ۵px + گلوی طلایی.
  - **سازگاری RTL:** همه با inset-inline / grid؛ `justify-content: space-between` در head کارت.
  - از قالبِ خطاهای قبلی پرهیز شد: تیتر/متنِ کارتِ پهن هرکدام `grid-area` خودشان (تداخلِ ردیفِ مشترک باگِ اولیه بود و اصلاح شد)؛ `transform-origin: inline-start` نامعتبر بود و با درصد جایگزین شد.
- **پروب:** صفحهٔ خانه 200؛ ۶ کارت (اول/آخر = wide)، عرضِ کارتِ پهن ۶۱۱px و عادی ~۲۹۷px در ۱۲۹۶px، ۶/۶ فیگورِ hairline مونتِ 5:4 (نسبت 1.250)، بدونِ سرریزِ افقی، هیچ اثری از `why-bus/why-trace/why-board` نمانده؛ اسکرین‌شاتِ دسکتاپ هم تأیید بصریِ بنتو را داد.
- **کامیت:** `03cec43` (sections.css -223/+237 تقریباً خطِ به خط بازنویسیِ بلوکِ oldبرد، و `_why.html`).
- **هنوز کامیت‌نشده:** لابِ دمو (`static/demo/` با ۶ طرحِ zdog/isometric/troika) هنوز untracked است تا نظرِ کاربر بگیرد.

