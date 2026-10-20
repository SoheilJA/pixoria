
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
