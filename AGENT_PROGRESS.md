# Agent Progress — Pixoria

به‌روزرسانیِ این فایل بعد از هر تسک، تا جلسهٔ بعدی از همان نقطه ادامه دهیم.

شاخهٔ فعلی: `feature/rocket-redesign` (برای PR به `main`)

## تسک‌های انجام‌شده در این جلسه

### ۱. حذف کامل بخش پروپوزال ✅
کاربر: «بخشی که مربوط به ارسال پروپوزال هست رو کلا پاک کن نیازی بهش ندارم»

کامیت: `1fef995 feat: remove proposal section entirely`

پاک شد:
- مدل‌های `Proposal`, `ProposalStat`, `ProposalProblem`, `ProposalService` از `apps/core/models.py`
- ویوی `proposal` از `apps/core/views.py` (و ایمپورت `Proposal` و `get_object_or_404`)
- ادمینِ `ProposalAdmin` و سه اینلاین از `apps/core/admin.py`
- مسیر `proposal/<slug:slug>/` از `config/urls.py`
- قالب `templates/core/proposal.html` (کلاً حذف فایل)
- بلوکِ پروپوزال در `scripts/render_check.py`
- مایگریشنِ `apps/core/migrations/0013_delete_proposal_models.py` برای حذف جداول

**نکته:** مایگریشن ساخته شد ولی `manage.py migrate` هنوز اجرا نشده. در جلسهٔ بعد باید اجرا شود تا جداول از دیتابیس حذف شوند.

### ۲. فشرده‌سازی تصاویر نمونه‌کار به WebP ✅ (نسخهٔ اول)
کاربر: «میخوام تصاویر نمونه کار ها که بارگذاری میشن با حفظ کیفیت به کمترین حجم تبدیل بشن و با فرمت webP. تصاویر نمونه کار های برنامه نویسی و طراحی سایت به صورت افقی و مستطیل هستن چون اسکرین شات از هیروسکشن سایت هست ولی برای همه انواع خدمات گرافیکی و لوگو و ... به صورت مربعی هست»

**تصمیمِ گرفته‌شده (با پرسش از کاربر):** کارت‌ها **نسبت طبیعیِ تصویرِ خودشان** را حفظ می‌کنند (افقی مستطیل برای سایت‌سازی، مربعی برای لوگو/گرافیک) — نه کانواسِ ۴/۳ یکسان، نه برش.

کامیت: `18a0fa9 feat: compress portfolio images to WebP on upload`

فایل‌های ادیت‌شده:
- **`apps/core/image_utils.py`** (جدید) — تابع `compress_to_webp()`:
  - کیفیت ۸۵، متد ۴، حداکثر پهنای ۱۶۰۰px (با حفظ نسبت)
  - تصاویر شفاف (RGBA/LA/P) روی پس‌زمینهٔ تیرهٔ سایت `(10,10,12)` ترکیب می‌شوند تا حاشیهٔ روشن دور لوگوها نماند
  - نام فایل را به `.webp` تبدیل می‌کند (پسوندِ تصادفیِ Django مثل `_XOwXvqo` حفظ می‌شود)
- **`apps/portfolio/models.py`** — `Portfolio.save()` و `ProjectImage.save()` تصویر را موقع آپلود به WebP تبدیل می‌کنند (اگه از قبل WebP نباشد)
- **`templates/components/_project_card.html`** — `aspect-[4/3] ... object-cover` → `h-auto w-full object-cover` (برش حذف)
- **`templates/portfolio/detail.html`** — تصویر اصلی `aspect-[16/9]` و گالری `aspect-[4/3]` → `h-auto w-full object-cover`

### ۳. رفعِ خطای `runserver` ✅
کاربر: «مشکل چیه؟»

خطا: `ModuleNotFoundError: No module named 'whitenoise'`

انجام شد:
- نصبِ `whitenoise==6.12.0` در venv (در `requirements.txt` بود ولی نصب نبود)
- اجرای `manage.py migrate` → مایگریشنِ `core.0013_delete_proposal_models` اعمال شد و جداولِ پروپوزال از دیتابیس حذف شدند
- `manage.py check` پاس شد؛ تستِ `runserver`: `/` و `/portfolio/` هر دو `200`

### ۴. مارکویی برندها + مارکویی ابزارها ✅
کاربر: «در صفحه اصلی سکشنی که برندهایی که به ما اعتماد کردن به صورت مارکویی رد میشن میخوام فقط اسم برند نوشته شده باشه و اسم برند هم به صورت داینامیک از اسم برندی که زمان بارگذاری نمونه کارها از ادمین خونده بشه. همچنین دایره حذف بشه. و بعدش مارکویی بهترین ابزارها، همون که دوتا مارکویی داره که خلاف جهت همدیگه حرکت میکنن مشکل داره»

کامیت: `0cc5e88 feat: trusted marquee reads brand names from portfolio, fix tech marquee`

**الف) سکشن برندها (`#trusted`):**
- نشانِ دایره‌ای (`brand-mark` + `brand-mark-gold/royal`) و پلاک (`brand-plate`) کلاً حذف شد
- حالا فقط `.brand-name` (متنِ سادهٔ نام برند) در مارکویی حرکت می‌کنه
- منبعِ داده از `ClientMarqueeItem` به `Portfolio.client_name` تغییر کرد — هر نمونه‌کاری که در ادمین بارگذاری بشه، برندش خودکار اینجا ظاهر می‌شه:
  - `apps/home/views.py`: کوئری `Portfolio.objects.exclude(client_name="").values_list("client_name", flat=True).distinct()`
  - ایمپورتِ `ClientMarqueeItem` از `apps/home/views.py` حذف شد
- `templates/home/sections/_trusted.html` بازنویسی شد
- CSS های `brand-plate`/`brand-mark*` از `static/src/input.css` پاک شدند؛ `.brand-name` حالا `flex: none` داره تا در مارکویی فشرده نشه

**ب) مارکویی ابزارها (`#tech`):**
- `dir="ltr"` به هر دو ردیفِ مارکویی در `templates/home/sections/_tech.html` اضافه شد (قبلاً فقط `#trusted` و `services/detail.html` داشتند؛ بدون اون در صفحهٔ RTL چیپ‌ها برعکس چیده می‌شدن)
- به‌جای `animation-direction: reverse`، keyframe صریح `@keyframes marquee-rev` (از `-50%` به `0`) ساختم تا پرشِ شروع از بین بره
- `flex: none` به `.marquee-group` اضافه شد

**نکته:** `npm run build` بعد از تغییر `input.css` زده شد (خروجی در `static/css/tailwind.css`). این فایل سرو می‌شه، نه `public/static/`.

### ۵. رفعِ منوی موبایل + ثابت‌کردنِ آیتم‌های منو ✅
کاربر: «منو موبایلی مشکل داره و انگار از سمت راست فاصله داره چون به سمت چپ فشرده شده و از کادر خارج شده، همینطور ترتیب المان های توی منو موبایلی رو به صورت ثابت قرار بده و نیازی نیست از طریق ادمین پنل نام و ترتیب و لینکش رو وارد کنم و کلا این منطق رو از مدل و ادمین حذف کن، همینطور الان همه المان های توی منو در پاپ اپ منو موبایلی جلوشون یک فلش به سمت چپ دارن که درست نیست فقط خدمات باید فلش به سمت پایین داشته باشه و وقتی روش کلیک میشه اکستند بشه و خدمات توش نمایش داده بشه»

**الف) دلیلِ واقعیِ کج بودنِ پنل (با CDP پیدا شد):**
کلاس `.glass` در `styles/input.css` موقعیت `position: relative` می‌داد. چون این بلوک **بدونِ `@layer`** بود و utilityهای Tailwind (`.absolute`) داخلِ `@layer utilities` قرار دارند، طبقِ قوانینِ cascade لایه‌ها، CSSِ بدونِ لایه همیشه می‌برد. نتیجه: `.menu-panel.glass.absolute inset-x-4` در عمل `relative` محاسبه می‌شد → کلِ عرضِ viewport را می‌گرفت و در RTL فقط `right` اعمال می‌شد، یعنی پنل ۱۶px به سمتِ چپ می‌رخت (در ۳۶۰px: `left=-16, right=340`).
- **توجه:** این باگ **فقط منوی موبایل نبود** — هر ترکیبِ `glass` + `absolute` همین مشکل را داشت (بج‌های شیشه‌ای سکشن خدمات، کپشن‌های about، بج `services/detail`).
- **رفع:** بلوکِ `.glass` / `.glass-light` / `::before`‌هایشان داخلِ `@layer components` قرار داده شد. ترتیبِ لایه‌ها از خطِ `@import "tailwindcss"` (`theme, base, components, utilities`) ثابت می‌ماند، پس حالا `.absolute` می‌برد.
- بعد از `npm run build` حتماً باید `manage.py collectstatic --noinput` زده شود — فایلِ سرو‌شده `public/static/css/tailwind.<hash>.css` است (با `CompressedManifestStaticFilesStorage`).

**ب) آیتم‌های منو ثابت شدند (حذفِ منطقِ دیتابیس):**
- فایلِ جدید **`apps/core/nav.py`** → ثابتِ `NAV_ITEMS`: لیستِ دیکشنری‌های `{"title", "url"}` با ترتیبِ ثابت (خانه، نمونه‌کارها، خدمات، بلاگ، درباره ما، تماس). **منبعِ واحدِ همِ منوی دسکتاپ و همِ منوی موبایل** تا عنوان/لینک دو جا تکرار نشود.
- `apps/core/context_processors.py`: `"nav_items": NAV_ITEMS` (به‌جای کوئری دیتابیس).
- **حذف شد:** مدل `NavItem` از `apps/home/models.py`، `NavItemAdmin` از `apps/home/admin.py`، بخشِ seed کردنِ منو در `seed_home_content.py` (به‌جز CTA).
- مایگریشنِ `apps/home/migrations/0014_delete_navitem.py` ساخته و **اعمال شد** (`manage.py migrate home`).
- قالبِ `_header.html` تغییری نکرد — هنوز `{% for item in nav_items %}` می‌چرخد و `{% nav_url item.url %}` را resolve می‌کند (دیکشنری در قالب با `item.title` / `item.url` درست کار می‌کند).

**ج) فلش‌های منوی موبایل:**
- فلشِ چپ (`chevron-left`) از همهٔ آیتم‌های سطحِ اول و از لینک‌های زیرمنوی خدمات حذف شد؛ `justify-between` هم از آن‌ها رفت.
- فقط «خدمات» دکمهٔ `m-chevron` با `chevron-down` دارد (آکاردئونِ `data-m-accordion`، منطقِ JS در `static/js/pixoria.js` دست‌نخورده باقی ماند).

**گزینه‌های ایجاد‌شده/تغییر یافته:**
- `scripts/_menu_check.py` دو چکِ جدید گرفت: «پنل افقی در viewport قرینه است» (این رگرسیون را می‌گیرد) و «فقط یک دکمهٔ آکاردئون وجود دارد و آیتم‌های ساده فلش ندارند». نتیجه: **ALL PASS** در ۳۹۰px و ۳۲۰px.
- `_menu_probe.py` و `_menu_shots.py` اسکریپت‌های موقتی بودند و حذف شدند.

**نکته:** این محیط ورودی multimodal نمی‌پذیرد — اسکرین‌شات‌ها خوانده نمی‌شوند؛ تأیید با اعدادِ CDP و رندرِ قالب انجام شد.

## کارهای باقی‌مانده (اولویت به ترتیب)

### ضروری — قبل از کامل‌شدن تسک تصاویر
1. ~~اجرای مایگریشنِ حذف پروپوزال~~ ✅ انجام شد
   ~~مايگریشن ۰۰۱۴ (حذف NavItem) هم ساخته و اعمال شد~~ ✅
2. **بررسیِ بصریِ بج‌های شیشه‌ای:** با رفعِ تداخلِ `.glass` و `absolute` (تسک ۵)، بج‌های `glass absolute` در `_services.html` (۸۴، ۱۲۰، ۲۰۲، ۲۰۵)، `_about.html` (۶۵، ۷۱)، `about.html` (۲۸۳، ۴۲۵) و `services/detail.html` (۳۳۴) حالا واقعاً absolute هستند و جایگاهشان نسبت به قبل (که اشتباهاً relative بودند) تغییر کرده. در مرورگر باید چک بشن که روی کارت/تصویر قرار گرفته باشند.
3. **تستِ واقعیِ فشرده‌سازی:** آپلود یک JPEG/PNG در ادمین و بررسی:
   - فایل در `public/media/portfolio/` با پسوند `.webp` ذخیره می‌شود؟
   - حجم کاهش یافته و نسبت ابعاد حفظ شده؟
   - تصاویرِ موجود (الان دو تا در دیتابیس هست: `images.jpg` ۶۷۸×۴۵۲ و `images_XOwXvqo.jpg` ۵۵۴×۵۵۴) هنوز تبدیل نشده‌اند — نیاز به اجرای دستی یا یک مایگریشن/دستورِ تبدیلِ تصاویرِ قدیمی
5. **بررسیِ بصریِ کارت‌ها:** چون ارتفاع کارت‌ها حالا متغیر است، گریدِ سه‌ستونی در `templates/portfolio/list.html:118` و `templates/home/sections/_portfolio.html:56` ممکن است ردیف‌ها را با ارتفاع‌های نابرابر پر کند (رفتار masonry). باید در مرورگر نگاه شود که زشت نشده باشد. اگر خراب است، گزینه‌ها: CSS masonry، یا `items-start` روی گرید.
6. **سایر تصاویر سایت:** کاربر فقط نمونه‌کارها را گفت، ولی `ImageField` های دیگری هم هستن که هنوز تبدیل نمی‌شوند:
   - `apps/blog/models.py`: `avatar` (خط ۳۹)، `cover_image` (خط ۷۷)
   - `apps/services/models.py`: `og_image` (۲۱۳)، `image` (۲۹۳)، `author_image` (۶۷۵)، `video_poster` (۶۹۵)
   - `apps/core/models.py`: `image` (۳۶۲)
7. **بررسیِ بصریِ مارکویی‌ها در مرورگر واقعی:** من نتونستم تصاویر را ببینم (محیط multimodal نداره)؛ تغییرات منطقی بودن ولی باید با چشم چک بشن. به‌خصوص اینکه آیا ردیف reverse هم‌اکنون روان حرکت می‌کنه.

### تصمیماتِ باز
- **مدل `ClientMarqueeItem`:** الان فقط صفحهٔ درباره (`apps/core/views.py:87` و `templates/core/about.html`) ازش استفاده می‌کنه. آیا اون هم باید از `Portfolio.client_name` بخونه و مدل کلاً حذف بشه؟ از کاربر پرسیده شد، جواب نداده.
- نام برندهای فعلی در دیتابیس هنوز نمونه‌های تستی هستن («احمدی»، «مشتری ۲») — با بارگذاریِ نمونه‌کارهای واقعی در ادمین، مارکویی خودکار پر می‌شه.

### نکاتِ فنی
- `requirements.txt` شامل `pillow==12.3.0` است (نصب شده در `venv`)
- `venv/Scripts/python manage.py check` پاس شد (هیچ خطایی نیست)
- کلاسیفایرِ Bash گاهی قطع می‌شود — اگر دوباره قطع شد، با Edit ادامه دهید
- تنظیمات: `config/settings.py`، media در `public/media/`، آدرس `/public/media/`
