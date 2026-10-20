
### دنبالهٔ ۳۲ — وندورِ لوکالِ @lucasmarkes/hairline (v0.5.1، MIT)
- درخواستِ کاربر با فایلِ `hairline.txt` در روت: کتابخانهٔ `@lucasmarkes/hairline` کشف شد (۳۳ فیگورِ خطیِ ایزومتریکِ pointer-reactive: riffle/terrain/vault/terminal/turntable/…، خروجی SVG با نسبت ۵:۴، API فانکشنی `fig(el,{play:true})` + `update`/`destroy` — شبیه Svelte action.
- از رجیستری npm تاربال رسمی (v0.5.1) دانلود و `dist/index.js` (مینیفای، Pure ESM، **هیچ** import و وابستگی — react فقط peerِ اختیاریِ wrapper جدا) برداشته شد به `static/js/vendor/hairline.js` با بنرِ نسخه/لایسنس؛ خطِ `sourceMappingURL` حذف شد (map وندور نشد، ری‌اکت wrapper به دلیل vanilla بودنِ پروژه نیامد).
- `collectstatic` → هشِ `js/vendor/hairline.d2a5f17f7102.js`. پروبِ مرورگر روی `/about/`: import ماژولِ ۳۳ خروجی، رندرِ `riffle` در ۳ دایو (SVG 280×224)، `update({intensity})` و `destroy()` تمیز — سبز. یک گیر: cache ۴۰۴ِ مرورگر بعد از ری‌استارتِ سرور — با `?v=2` دور زده شد (نه مشکلِ پکیج، نه مشکلِ سرور).
- استفادهٔ عملی در قالب بعداً: `<script type="module" src="{% static %}">` یا `import()` داینامیک از `pixoria.js`. فایل `hairline.txt` روت مستقل ماند (کامیت نشد).
