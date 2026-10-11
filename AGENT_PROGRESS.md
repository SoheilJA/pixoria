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

## کارهای باقی‌مانده (اولویت به ترتیب)

### ضروری — قبل از کامل‌شدن تسک تصاویر
1. **اجرای مایگریشنِ حذف پروپوزال:** `venv/Scripts/python manage.py migrate`
2. **تستِ واقعیِ فشرده‌سازی:** آپلود یک JPEG/PNG در ادمین و بررسی:
   - فایل در `public/media/portfolio/` با پسوند `.webp` ذخیره می‌شود؟
   - حجم کاهش یافته و نسبت ابعاد حفظ شده؟
   - تصاویرِ موجود (الان دو تا در دیتابیس هست: `images.jpg` ۶۷۸×۴۵۲ و `images_XOwXvqo.jpg` ۵۵۴×۵۵۴) هنوز تبدیل نشده‌اند — نیاز به اجرای دستی یا یک مایگریشن/دستورِ تبدیلِ تصاویرِ قدیمی
3. **بررسیِ بصریِ کارت‌ها:** چون ارتفاع کارت‌ها حالا متغیر است، گریدِ سه‌ستونی در `templates/portfolio/list.html:118` و `templates/home/sections/_portfolio.html:56` ممکن است ردیف‌ها را با ارتفاع‌های نابرابر پر کند (رفتار masonry). باید در مرورگر نگاه شود که زشت نشده باشد. اگر خراب است، گزینه‌ها: CSS masonry، یا `items-start` روی گرید.
4. **سایر تصاویر سایت:** کاربر فقط نمونه‌کارها را گفت، ولی `ImageField` های دیگری هم هستن که هنوز تبدیل نمی‌شوند:
   - `apps/blog/models.py`: `avatar` (خط ۳۹)، `cover_image` (خط ۷۷)
   - `apps/services/models.py`: `og_image` (۲۱۳)، `image` (۲۹۳)، `author_image` (۶۷۵)، `video_poster` (۶۹۵)
   - `apps/core/models.py`: `image` (۳۶۲)
   - تازه‌ترین قالب‌های `_project_card` و `detail.html` باید در پروژهٔ کامل بررسی شوند.

### نکاتِ فنی
- `requirements.txt` شامل `pillow==12.3.0` است (نصب شده در `venv`)
- `venv/Scripts/python manage.py check` پاس شد (هیچ خطایی نیست)
- کلاسیفایرِ Bash گاهی قطع می‌شود — اگر دوباره قطع شد، با Edit ادامه دهید
- تنظیمات: `config/settings.py`، media در `public/media/`، آدرس `/public/media/`
