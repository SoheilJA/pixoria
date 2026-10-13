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

### ۶. جایگزینیِ Lucide با Font Awesome (لوکال + انتخاب از ادمین) ✅
کاربر: «آیکون های کتابخانه lucide محدود هستن و میخوام بجاش از فونت آوسام استفاده کنم اونم به همینصورت به حالت لوکال و با قابلیت انتخاب آیکون از طریق ادمین پنل [...] فایل های مربوط به lucide رو پاک کن و فونت آوسام رو دانلود و استفاده کن»

**تصمیمات (با پرسش از کاربر):** Font Awesome **6 Free** (`@fortawesome/fontawesome-free@^6.7.2` از npm، خودمیزبانی)، سبکِ پیش‌فرض **solid**، آیکون‌های برند خودکار `fa-brands`.

**چرا webfont به‌جای SVG sprite:** فونت شاملِ همهٔ آیکون‌های رایگان است، پس هر چیزی که ادمین در پیکر انتخاب کند **فوراً** روی سایت می‌افتد — مرحلهٔ `manage.py sync_icons` حذف شد. گلیف‌ها از `currentColor` استفاده می‌کنند، پس تمام کلاس‌های رنگ (`text-gold` و غیره) بدون تغییر کار می‌کنند.

فایل‌های جدید:
- **`scripts/build_fontawesome.js`** — از `node_modules` کپی می‌کند به `static/fontawesome/`: `css/all.min.css` (فقط سورس‌های woff2 نگه داشته می‌شوند)، چهار `webfonts/*.woff2`، و `icons.json` (فهرستِ ۲۰۶۰ آیکونِ رایگان، دسته‌بندی‌شده بر اساس سبک — مرجعِ ولیدیشنِ پایتون). `static/admin/js/fa_icons.js` (`window.__FA_ICONS`) را هم برای پیکر می‌سازد.
  - **ولیدیشنِ زمانِ بیلد:** نگاشتِ `LUCIDE_TO_FA` و تمامِ `{% icon "x" %}`های قالب‌ها را در برابر فهرستِ رسمی چک می‌کند؛ اگر یک نام معادلِ رایگان نداشته باشد، بیلد **fail** می‌شود (`npm run build:icons`).
- **`scripts/_fa_render_check.py`** و **`scripts/_admin_icon_check.py`** — تأیید با CDP (مرورگر واقعی). صفحه‌های اصلی + ادمین: لاگین، باز شدنِ پاپ‌آپِ پیکر، ۲۴۰ آیکون در گرید، فیلترِ جستجو، انتخاب، پیش‌نمایشِ گلیف با اندازهٔ غیرصفر، هشدارِ نامِ نامعتبر. **ALL PASS**.

فایل‌های ادیت‌شده:
- **`apps/core/icon_utils.py`** — بازنویسی کامل: دیکشنریِ `LUCIDE_TO_FA` (۹۰ نام)، `map_icon_name()`، `icon_style()` (brands خودکار)، `validate_icon_name()` (چک در برابر `icons.json`)، `icon_preview_html()` → `<i class="fa-solid fa-x">`. `IconPickerWidget` حالا CSS فونت آوسام را در `Media` دارد.
- **`apps/core/templatetags/icon_tags.py`** — خروجی `<svg><use>` → `<i class="fa-solid fa-x" style="font-size:...">`. **سینتکسِ قالب‌ها دست‌نخورده است**؛ کلاس‌های `h-N/w-N` به inline font-size تبدیل می‌شوند (آیکون inline است و height/width اثر ندارد — `h-1/2` و `h-full` عمداً دست‌نخورده می‌مانند). ~۱۳۰ نقطهٔ استفاده در قالب‌ها نیاز به ویرایش نداشتند.
- **`apps/home/models.py`**، `apps/core/models.py`، `apps/portfolio/models.py`، `apps/services/models.py`، `apps/contact/models.py` — `ICON_HELP`ها و مثال‌ها (lucide.dev → fontawesome.com)، `default`ها (`sparkles` → `wand-magic-sparkles`، `message-circle` → `comment`).
- **`static/admin/js/icon_picker.js`** — رندرِ سلول‌ها `<i class="fa-...">`، خواندن `__FA_ICONS`، حذفِ منطقِ «هنوز sync نشده».
- **`templates/base.html`** — `<link>` فونت آوسام بعد از `tailwind.css`.
- **`templates/core/about.html`** + `styles/input.css` — آیکونِ سیاره‌های صحنهٔ فضایی: `h-1/2 w-1/2` → اندازه از `--size` (`font-size: calc(var(--size) * 0.5)`) چون هر مدار اندازهٔ متفاوتی دارد.
- **`templates/components/README.md`** و `package.json` (`build:icons`).

مایگریشن‌های داده (۵ تا، **همگی اعمال شدند**): `core.0014`، `home.0015`، `portfolio.0008`، `services.0012`، `contact.0005` — هر کدام `RunPython` برای نگاشتِ مقادیرِ ذخیره‌شده + `AlterField` برای defaults/help_text. نام‌های ناشناخته دست‌نخورده می‌مانند (fail-safe). تمام مقادیرِ دیتابیس بعد از مهاجرت نام‌های معتبر فونت آوسام هستند.

حذف شد:
- `static/icons/lucide.sprite.svg`، `static/icons/lucide.full.sprite.svg` (و دایرکتوری `static/icons/`)
- `static/admin/js/lucide_full_icons.js`
- `scripts/build_icon_sprite.js`
- `apps/core/management/commands/sync_icons.py`
- `lucide-static` از npm

**سه تا باگ در حینِ تأیید پیدا و رفع شد:**
1. خروجیِ `{% icon %}` HTML-escape می‌شد (`mark_safe` در تگِ جدید جا افتاده بود) — آیکون‌ها به‌شکلِ `&lt;i class=...` در صفحه می‌آمدند. رفع با `mark_safe`.
2. `h-1/2` با regex به `4px` تبدیل می‌شد (فقط `1` خوانده می‌شد). ریش: regex فقط اعدادِ تمام‌شده را می‌پذیرد؛ اندازهٔ این نقطه به CSS منتقل شد.
3. **پیکرِ ادمین کاملاً مُرده بود:** ادمینِ جنگو `{{ media }}` را داخلِ `<head>` رندر می‌کند، پس `icon_picker.js` قبل ازِ وجودِ DOM اجرا می‌شد و `querySelectorAll("[data-icon-picker]")` خالی بود. رفع: `DOMContentLoaded` + `MutationObserver` (برای اینلاین‌های داینامیک) + گاردِ `data-ip-ready`.

**نکتهٔ مهم:** ادمین فایل‌های استاتیک را از `public/static/` (STATIC_ROOT) سرو می‌کند، نه `static/`. بعد از هر تغییر در `static/admin/js/` یا `static/admin/css/` باید `manage.py collectstatic --noinput` زده شود. همچنین پروفایلِ Chromeِ اسکریپت‌های بررسی (`_fa_render_check.py` و `_admin_icon_check.py`) بین اجراها دوباره استفاده می‌شود — اگر فایلِ استاتیک را عوض کردید، پروفایل‌ها را پاک کنید تا کشِ مرورگر invalidate شود.

### ۷. محویِ لبه‌های کاروسل + رابطِ شکستهٔ اسلایدرِ یک‌کارته ✅
این کار در حال انجام بود ولی هنوز کامیت نشده بود (فقط روی working tree).

کامیت: `0ae5d08 feat: edge fade on carousels, hide slider controls for a single card`

- کلاسِ جدید **`.edge-fade`** در `styles/input.css` — همان mask-imageِ مارکویی ولی با نوارِ باریک‌تر (۶٪)، چون کارت‌های کاروسل در حالتِ استراحت روی لبه می‌ایستند و نباید مثلِ چیپِ متحرک محو شوند.
- `templates/components/carousel.html` یک پارامترِ `track_class` گرفت؛ `articles_carousel.html` و `testimonials_slider.html` آن را پاس می‌دهند. **کاروسلِ نمونه‌کارها دست‌نخورده ماند** (همان shell را استفاده می‌کند ولی `track_class` نمی‌گیرد).
- **باگِ رابطِ کاربری:** اسلایدرِ نظرات در دیتابیسِ فعلی فقط **یک کارتِ قابلِ نمایش** دارد — دو نظرِ ویدیویی/صوتی فایلِ رسانه‌ای ندارند و فیلترِ `playable` در `testimonial_tags.py` حذفشون می‌کنه. نتیجه: دکمه‌های قبلی/بعدی و راهنمای «بکشید…» بدونِ اینکه کاری بکنند نمایش داده می‌شدند. حالا دکمه‌ها و راهنما با `{% if testimonials|length > 1 %}` محاصره شدند. JS از قبل با نبودِ `[data-slider-dots]` early-return می‌کند (`static/js/pixoria.js:604`)، پس autoplay و drag هم متوقف می‌شوند.
- تأیید: `scripts/_carousel_fade_check.py` (CDP) — ALL PASS. این اسکریپت حالا data-aware است: وقتی فقط یک کارت هست، به‌جای «اسکرول نمی‌شه»، «کنترل‌ها چاپ نشدند» را چک می‌کند.

### ۸. بررسیِ بصریِ کارهای قبلی با CDP ✅
این محیط **multimodal قبول نمی‌کند** (اسکرین‌شات خوانده نمی‌شود)؛ بررسی‌ها با اندازه‌گیریِ هندسی در مرورگرِ واقعی انجام شد. اسکریپت‌ها در `scripts/_*.py` (gitignore شده‌اند، محلی).

کامیت: `e6c25a9 feat: portfolio cards keep natural aspect, convert existing images to WebP`

**الف) بج‌های شیشه‌ای (تسک ۵ — تأیید نهایی):** ۶ بجِ `glass absolute` در صفحهٔ اصلی با CDP بررسی شدند. همه واقعاً `position: absolute` هستند (یعنی رفعِ تداخلِ `.glass`/`@layer` کار کرده) و **هیچ بیرون‌زدگیِ افقی** ندارند. بیرون‌زدگیِ عمودیِ ۸–۱۲px کاملاً عمدی است (کلاس‌های `-top-2`/`-top-3`/`-bottom-3` در `_services.html`).
- نکتهٔ دیباگ: نامِ مشخصه در `CSSStyleDeclaration` به‌جای `fillMode` باید `animationFillMode` باشد؛ `fillMode` مقدار `undefined` برمی‌گرداند و `JSON.stringify` کلید را کلاً حذف می‌کند.

**ب) مارکویی‌ها (تسک ۴ — تأیید نهایی):** ۳ ردیف: `marquee` ۶۲s (برندها)، `marquee` ۴۰s، `marquee-rev` ۴۰s. همه `dir="ltr"`، `overflow: hidden`، `.marquee-group` با `flex: 0 0 auto` (یعنی `flex: none`) و transform‌ها غیرِ همانی یعنی انیمیشن در حالِ اجراست. fill-mode نیازی نیست چون انیمیشن بی‌نهایت و فوری است.

**ج) گریدِ کارت‌ها (تسک ۵ — باگِ واقعی پیدا و رفع شد):** کارتِ اول `images.jpg` (نسبتِ ۱.۵) در کنار کارتِ دوم مربعی (نسبتِ ۱) در یک ردیفِ `stretch` می‌ایستاد: کارتِ اول به ۳۹۵px کشیده می‌شد در حالی که تصویرش ۲۶۲px بود → **۱۳۳px فضای مرده** زیر تصویر، و کپشن (`absolute inset-0` با `justify-content: flex-end`) ۱۳۳px پایین‌تر از پایینِ تصویر می‌نشست.
- **رفع:** `items-start lg:items-start` روی گرید در `templates/portfolio/list.html` و `templates/home/sections/_portfolio.html`. حالا هر کارت ارتفاعِ تصویرِ خودش را دارد (اندازه‌گیری: gap=2px برای هر دو کارت).

**د) CLS (یک باگِ جدید):** روی صفحهٔ اصلی، قبل از بارگذاریِ تصویرِ lazy، کارت فقط **۲px** بود (`natural=0x0`) و بعد از بارگذاری به ۲۶۴px می‌پرید — یعنی layout shift، در سایتی که خودش بجِ «۹۹/۱۰۰ · Core Web Vitals» دارد!
- **رفع:** `width="{{ project.image.width }}" height="{{ project.image.height }}"` به `<img>` در `_project_card.html` اضافه شد (از فرادادهٔ فایل via `ImageFieldFile`، بدون تغییرِ مدل). حالا حتی قبل از بارگذاریِ تصویر، جا رزرو می‌شود (۲۶۴px).

### ۹. تبدیلِ تصاویرِ موجود به WebP ✅
کامیت: `e6c25a9` (همان کامیت)

- **`compress_to_webp_if_smaller()`** جدید در `apps/core/image_utils.py` — اگر نسخهٔ WebP حداقل ۲٪ کوچک‌تر نشود، `None` برمی‌گرداند. دلیل: `images.jpg` (۶۷۸×۴۵۲، ۳۸KB) که قبلاً فشرده شده، با quality ۸۵ به **۴۸KB** می‌رسید (۲۹٪ بزرگ‌تر!). حالا `Portfolio.save()` و `ProjectImage.save()` از این تابع استفاده می‌کنند، نه از `compress_to_webp` مستقیم.
- **کامندِ جدید `manage.py compress_images`** (`apps/portfolio/management/commands/compress_images.py`) — تصاویرِ روی دیسک را تبدیل می‌کند. dry-run پیش‌فرض، `--write` برای اعمال. فایلِ قدیمی را حذف می‌کند و تفاوتِ حجم را گزارش می‌دهد.
  - **سه تا باگِ پیچیده در حینِ نوشتن پیدا شد:**
    1. **`FieldFile.save(save=False)` فقط ذخیرهٔ *مدل* را رد می‌کند، ولی فایل را روی دیسک می‌نویسد!** پس dry-runِ اول واقعاً فایل می‌ساخت (چند فایلِ یتیمِ `.webp` در `public/media/portfolio/` ساخته شد و پاک شدند). حالا در حالتِ خشک، فقط `compressed.size` و `storage.get_available_name()` خوانده می‌شود و هیچ I/O‌ای انجام نمی‌شود.
    2. **PIL فایلِ مبدا را باز نگه می‌دارد** و ویندوز اجازهٔ حذفِ فایلِ باز را نمی‌دهد. رفع: `source.close()` قبل از `storage.delete()`.
    3. نامِ فایل باید از `ContentFile`ِ بازگشتی خوانده شود، نه از نامِ قدیمی — وگرنه محتوای WebP با پسوندِ `.jpg` ذخیره می‌شد.
  - **اجرای واقعی:** `images_XOwXvqo.jpg` (۱۹KB) → `images_XOwXvqo.webp` (**۹KB، ۵۴٪ کوچک‌تر**)، فایلِ قدیمی حذف شد. `images.jpg` رد شد (WebP بزرگ‌تر می‌شد).
- **نکتهٔ فنی برای ویندوز:** کنسولِ ویندوز cp1252 است و فارسی را پشتیبانی نمی‌کند؛ کامندهای مدیریت را با `PYTHONUTF8=1 venv/Scripts/python manage.py ...` اجرا کنید.

## کارهای باقی‌مانده (اولویت به ترتیب)
1. ~~اجرای مایگریشنِ حذف پروپوزال~~ ✅ انجام شد
   ~~مايگریشن ۰۰۱۴ (حذف NavItem) هم ساخته و اعمال شد~~ ✅
2. ~~بررسیِ بصریِ بج‌های شیشه‌ای~~ ✅ تسک ۸-الف (CDP: همگی absolute، بدون سرریزِ افقی)
3. ~~تستِ واقعیِ فشرده‌سازی~~ ✅ تسک ۹ — کامند نوشته شد، اجرا شد، ۱۹KB→۹KB
5. ~~بررسیِ بصریِ کارت‌ها~~ ✅ تسک ۸-ج — باگِ ۱۳۳px پیدا و رفع شد (`items-start`)
7. ~~بررسیِ بصریِ مارکویی‌ها~~ ✅ تسک ۸-ب (CDP: ۳ ردیف، marquee-rev فعال، در حالِ اجرا)

6. **سایر تصاویر سایت (تنها موردِ باز):** کاربر فقط نمونه‌کارها را گفت، ولی `ImageField` های دیگری هم هستن که هنوز تبدیل نمی‌شوند:
   - `apps/blog/models.py`: `avatar` (خط ۳۹)، `cover_image` (خط ۷۷)
   - `apps/services/models.py`: `og_image` (۲۱۳)، `image` (۲۹۳)، `author_image` (۶۷۵)، `video_poster` (۶۹۵)
   - `apps/core/models.py`: `image` (۳۶۲)
   - پیاده‌سازی مثلِ تسک ۹ است: `compress_to_webp_if_smaller` در `save()` هر مدل + اضافه‌کردنِ فیلد به `FIELDS` در `compress_images.py`. **از کاربر پرسیده نشده** — آیا دامنهٔ فشرده‌سازی به همهٔ تصاویر سایت گسترش یابد؟
   - **دقت:** `og_image` برای کارتِ شبکه‌های اجتماعی استفاده می‌شود؛ WebP توسط اکثرِ پلتفرم‌ها پشتیبانی می‌شود ولی Twitter/X در برخی موارد هنوز JPEG ترجیح می‌دهد.

### تصمیماتِ باز
- **مدل `ClientMarqueeItem`:** الان فقط صفحهٔ درباره (`apps/core/views.py:87` و `templates/core/about.html`) ازش استفاده می‌کنه. آیا اون هم باید از `Portfolio.client_name` بخونه و مدل کلاً حذف بشه؟ از کاربر پرسیده شد، جواب نداده.
- نام برندهای فعلی در دیتابیس هنوز نمونه‌های تستی هستن («احمدی»، «مشتری ۲») — با بارگذاریِ نمونه‌کارهای واقعی در ادمین، مارکویی خودکار پر می‌شه.

### نکاتِ فنی
- `requirements.txt` شامل `pillow==12.3.0` است (نصب شده در `venv`)
- `venv/Scripts/python manage.py check` پاس شد (هیچ خطیری نیست)
- کلاسیفایرِ Bash گاهی قطع می‌شود — اگر دوباره قطع شد، با Edit ادامه دهید
- تنظیمات: `config/settings.py`، media در `public/media/`، آدرس `/public/media/`
- **این محیط multimodal نیست** — اسکرین‌شات خوانده نمی‌شود. بررسی‌های بصری با CDP و اندازه‌گیریِ هندسی انجام شوند (الگو در `scripts/_geometry_check.py` و `scripts/_cardheight_check.py`).
- بعد از هر تغییر در `styles/input.css`: `npm run build` و سپس `manage.py collectstatic --noinput`.
- پروفایل‌های Chromeِ اسکریپت‌های بررسی (`.*-chrome-profile/`) اگر فایلِ استاتیک عوض شد باید پاک شوند تا کش invalidate شود.
- **`FieldFile.save(name, content, save=False)` فایل را روی دیسک می‌نویسد** — فقط ذخیرهٔ مدل را رد می‌کند. برای dry-run واقعی، اصلاً صدا نزنید.
