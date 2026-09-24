# Pixoria — بازطراحی فرانت‌اند بر اساس مرجع Rocket

منبع المان‌ها: `_reference/rocket-home.html` (تک‌فایل تأییدشده؛ منبع است، نه قالب نهایی — المان‌ها بازاستفاده می‌شوند).
قواعد سخت: بک‌اند (views/models/forms/urls/settings) دست‌نخورده. همه‌ی دارایی‌ها **لوکال** (بدون هیچ CDN). سایت کاملاً فارسی/RTL. Tailwind با build CLI (static/src/input.css). متن‌ها از دیتابیس/context، نه از JS.

## چک‌لیست فازها (✅ = انجام‌شده)

- [x] فاز ۰: بررسی پروژه + گزارش و نقشه‌ی فایل‌ها
- [x] برنچ `feature/rocket-redesign` + اسنپ‌شات legacy در `templates/_legacy/`
- [x] بازنویسی AGENTS.md (این فایل)
- [ ] فاز ۱: بنیاد — base.html، includes، site.css، core/*.js (تم/صدا/منو/ریل/کرسر/تایپ‌رایتر)، دارایی‌های لوکال (GSAP 3.12.5 + فونت‌ها)
- [ ] فاز ۲: موتور صحنه (engine/scene-engine.js) + کیت ambient (engine/ambient.js) + صفحه‌ی خانه (Hero شلوغ، داستان موشک، کنسول آرکید با حالت armed، leaderboard localStorage/نمونه)
- [ ] فاز ۳: صفحه‌ی خدمات + ۴ لندینگ (وب‌سایت/برنامه‌نویسی/لوگو/گرافیک)
- [ ] فاز ۴: درباره‌ی ما + تماس (فرم واقعی جنگو + toast messages)
- [ ] فاز ۵: بلاگ (آرشیو + مقاله از base_blog.html، ساده و خوانا)
- [ ] فاز ۶: QA نهایی (چک‌لیست معیار تکمیل + فهرست بخش‌های بدون مدل بک‌اند)

## معماری

- قالب‌ها: `templates/base.html` (شِل سینمایی)، `templates/base_blog.html` (بلاگ ساده)، `templates/includes/_*.html`، `templates/home/base_cinematic.html`
- استایل: `static/css/site.css` (توکن روز/شب + کامپوننت‌های مرجع)، توکن‌های Tailwind در `static/src/input.css` (@theme)
- JS: ES module در `static/js/` — `core/`، `engine/`، `stories/{page}.js` (lazy import در هر صفحه)، `arcade/`، `leaderboard.js`، `main.js`
- GSAP و فونت‌ها: `static/js/vendor/` و `static/fonts/` — لوکال
- هر صفحه فقط ماژول داستان خودش را dynamic import می‌کند؛ core مشترک است

## قواعد انتقال از مرجع

- `{% url %}` واقعی به‌جای لینک‌های نمونه؛ `{% csrf_token %}` و نام فیلدهای فرم بک‌اند حفظ شود
- متن تایپ‌رایتر و FAQ کامل در HTML (انیمیشن فقط بهبود تدریجی)
- داده‌ی JS از `{{ var|json_script:"..." }}`
- کرسر پیکسلی/ریل/پیش‌لودر فقط در صفحه‌های سینمایی؛ بلاگ ساده
- کنسول آرکید: کلیدها فقط بعد از کلیک/فوکوس (armed)، Esc آزاد می‌کند، خروج از دید = Pause
- کدهای تخفیف/رکورد فعلی فقط «نمونه/DEMO» — پیاده‌سازی سرور فقط با تأیید
- RTL با logical properties؛ اعداد HUD/کنسول ltr؛ canvas تزئینی aria-hidden؛ یک h1 در هر صفحه؛ reduced-motion رعایت شود
- کارکرد بدون JS باید محتوا را نشان دهد
