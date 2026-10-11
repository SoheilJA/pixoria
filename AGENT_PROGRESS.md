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

## کارهای باقی‌مانده (اولویت به ترتیب)

### ضروری — قبل از کامل‌شدن تسک تصاویر
1. ~~اجرای مایگریشنِ حذف پروپوزال~~ ✅ انجام شد
2. **تستِ واقعیِ فشرده‌سازی:** آپلود یک JPEG/PNG در ادمین و بررسی:
   - فایل در `public/media/portfolio/` با پسوند `.webp` ذخیره می‌شود؟
   - حجم کاهش یافته و نسبت ابعاد حفظ شده؟
   - تصاویرِ موجود (الان دو تا در دیتابیس هست: `images.jpg` ۶۷۸×۴۵۲ و `images_XOwXvqo.jpg` ۵۵۴×۵۵۴) هنوز تبدیل نشده‌اند — نیاز به اجرای دستی یا یک مایگریشن/دستورِ تبدیلِ تصاویرِ قدیمی
3. **بررسیِ بصریِ کارت‌ها:** چون ارتفاع کارت‌ها حالا متغیر است، گریدِ سه‌ستونی در `templates/portfolio/list.html:118` و `templates/home/sections/_portfolio.html:56` ممکن است ردیف‌ها را با ارتفاع‌های نابرابر پر کند (رفتار masonry). باید در مرورگر نگاه شود که زشت نشده باشد. اگر خراب است، گزینه‌ها: CSS masonry، یا `items-start` روی گرید.
4. **سایر تصاویر سایت:** کاربر فقط نمونه‌کارها را گفت، ولی `ImageField` های دیگری هم هستن که هنوز تبدیل نمی‌شوند:
   - `apps/blog/models.py`: `avatar` (خط ۳۹)، `cover_image` (خط ۷۷)
   - `apps/services/models.py`: `og_image` (۲۱۳)، `image` (۲۹۳)، `author_image` (۶۷۵)، `video_poster` (۶۹۵)
   - `apps/core/models.py`: `image` (۳۶۲)
5. **بررسیِ بصریِ مارکویی‌ها در مرورگر واقعی:** من نتونستم تصاویر را ببینم (محیط multimodal نداره)؛ تغییرات منطقی بودن ولی باید با چشم چک بشن. به‌خصوص اینکه آیا ردیف reverse هم‌اکنون روان حرکت می‌کنه.

### تصمیماتِ باز
- **مدل `ClientMarqueeItem`:** الان فقط صفحهٔ درباره (`apps/core/views.py:87` و `templates/core/about.html`) ازش استفاده می‌کنه. آیا اون هم باید از `Portfolio.client_name` بخونه و مدل کلاً حذف بشه؟ از کاربر پرسیده شد، جواب نداده.
- نام برندهای فعلی در دیتابیس هنوز نمونه‌های تستی هستن («احمدی»، «مشتری ۲») — با بارگذاریِ نمونه‌کارهای واقعی در ادمین، مارکویی خودکار پر می‌شه.

### نکاتِ فنی
- `requirements.txt` شامل `pillow==12.3.0` است (نصب شده در `venv`)
- `venv/Scripts/python manage.py check` پاس شد (هیچ خطایی نیست)
- کلاسیفایرِ Bash گاهی قطع می‌شود — اگر دوباره قطع شد، با Edit ادامه دهید
- تنظیمات: `config/settings.py`، media در `public/media/`، آدرس `/public/media/`
