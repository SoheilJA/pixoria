# 🗺️ نقشهٔ ساختار پروژهٔ پیکسوریا (PROJECT_STRUCTURE.md)

> **این فایل چیست؟** نقشهٔ کامل پروژه است: هر پوشه/فایل چه می‌کند، کجاست، چرا وجود دارد و
> «اگر خواستم X را عوض کنم، باید سراغ کدام فایل/مدل بروم». هدف این است که برای هر تغییر
> نیازی به گشتن در کل پروژه نباشد.
>
> ⚠️ **قاعدهٔ نگهداری:** هر وقت فایل/پوشهٔ مهمی اضافه، حذف یا جابه‌جا شد، همین فایل را هم به‌روز کنید.

---

## ۱) پروژه در یک نگاه

| مورد | مقدار |
| --- | --- |
| سایت | وب‌سایت آژانس دیجیتال «پیکسوریا» — استودیو طراحی سایت، برنامه‌نویسی و گرافیک در مشهد |
| زبان و جهت | فارسی، RTL کامل (`LANGUAGE_CODE=fa-ir`، `dir="rtl"`)، منطقهٔ زمانی `Asia/Tehran` |
| بک‌اند | Django 5.2 — پکیج‌ها در `requirements.txt` |
| دیتابیس | SQLite در `database/db.sqlite3` (پیش‌فرض) یا Postgres/MySQL از طریق `DATABASE_URL` در `.env` |
| فرانت | قالب‌های Django + Tailwind CSS v4 (کامپایل با CLI) + htmx + Lenis (اسکرول نرم) + آیکون‌های Lucide (اسپرایت لوکال) |
| ادمین | Django Admin با TinyMCE (RTL)، آیکون‌پیکر و ویجت انتخاب لوگو — آدرس عمداً مبهم: **`/who-are-you/`** |
| سرو استاتیک | WhiteNoise با gzip — بعد از هر تغییر استاتیک باید `collectstatic` اجرا شود (§۱۵) |
| انیمیشن | **هیچ GSAP ای در پروژه نیست** — همهٔ حرکت‌ها CSS خالص (`motion.css`، `sections.css`) و JS فقط «ماشه» می‌زند |
| دپلوی | Runflare (نصب CLI با `install.bat`) + `config/settings_production.py` + gunicorn |

---

## ۲) فایل‌ها و پوشه‌های روت

| مسیر | چیست و چرا هست |
| --- | --- |
| `manage.py` | نقطهٔ ورود Django؛ تنظیمات پیش‌فرض: `config.settings` |
| `requirements.txt` | پکیج‌های پایتون: Django، django-tinymce، pillow، whitenoise، python-dotenv، jdatetime، beautifulsoup4، … |
| `package.json` | ابزارهای Node. اسکریپت‌های مهم: `npm run build` و `npm run watch` → کامپایل `styles/input.css` به `static/css/tailwind.css`. دپندنسی‌های `opentype.js`/`sharp`/`wawoff2` فقط برای اسکریپت‌های ساخت برند هستند و به مرورگر نمی‌روند؛ `lenis` وابستگی ران‌تایم است |
| `.env.example` | نمونهٔ متغیرهای محیطی با توضیح فارسی. برای استفاده کپی کنید به `.env` (لوکال) یا `.env.production` (سرور)؛ فایل‌های واقعی gitignore شده‌اند |
| `.gitignore` | `venv/`، `.env*`، خروجی‌های `public/static` و `public/media`، `node_modules`، پروفایل‌های کروم تستی، فایل‌های موقت `scripts/_*.py` |
| `install.bat` | نصب CLI دپلوی «Runflare» روی ویندوز (نیازمند Run as Administrator). ربطی به کد سایت ندارد |
| `index.html` | ⚠️ **پروتوتایپ قدیمیِ استاتیک** (نسخهٔ قبل از Django؛ به `site.css`ای اشاره می‌کند که دیگر وجود ندارد). فقط مرجع است — بخشی از سایت فعلی نیست و تغییرش اثری ندارد |
| `prompt/` | دو اسکرین‌شات مرجع طراحی (`ryoku-dev.jpg`) — خروجی مورد انتظارِ ظاهری |
| `venv/` | محیط مجازی پایتون (gitignore شده). اجرای پایتون: `venv\Scripts\python` |
| `database/` | مکان فایل دیتابیس SQLite (`db.sqlite3`) — مسیرش در `config/settings.py` تعیین شده |
| `config/` | پکیج اصلی Django (تنظیمات و URLهای ریشه) → §۳ |
| `apps/` | شش اپ پروژه → §۴ تا §۸ |
| `templates/` | قالب‌های سایت → §۹ |
| `static/` | فایل‌های استاتیک **سورس** (CSS/JS/فونت/برند/آیکون) → §۱۰ |
| `styles/` | ورودی Tailwind (`input.css` = دیزاین‌سیستم سایت) → §۱۱ |
| `public/` | **خروجی build (نه سورس!)**: `public/static` = STATIC_ROOT (خروجی collectstatic)، `public/media` = MEDIA_ROOT (فایل‌های آپلودی ادمین). هر دو gitignore شده‌اند → §۱۲ |
| `scripts/` | اسکریپت‌های ابزاری → §۱۳ |

---

## ۳) پوشهٔ `config/` — تنظیمات و مسیرهای ریشه

| فایل | نقش |
| --- | --- |
| `config/settings.py` | تنظیمات اصلی (با کامنت فارسی). نکات کلیدی: لود `.env`؛ دیتابیس SQLite پیش‌فرض + پارس `DATABASE_URL` برای Postgres/MySQL؛ لیست اپ‌ها (`unfold` فعلاً کامنت است؛ `whitenoise.runserver_nostatic` باید **قبل از** `staticfiles` بماند)؛ کانفیگ TinyMCE (RTL + آپلود عکس به `/blog/tinymce-image-upload/`)؛ context processor به‌نشانی `apps.core.context_processors.site_context`؛ `STATIC_URL=/public/static/`، `STATIC_ROOT=public/static`، `MEDIA_ROOT=public/media`؛ `WHITENOISE_USE_FINDERS=False` (→ §۱۵) |
| `config/settings_production.py` | تنظیمات سرور: از settings ارث می‌برد، `DEBUG=False` را اجباری می‌کند، هدرهای امنیتی (HSTS یک‌ساله، SSL redirect، X-Frame=DENY). فعال‌سازی: `DJANGO_SETTINGS_MODULE=config.settings_production` |
| `config/urls.py` | نقشهٔ کل URLهای سایت (جدول پایین) + `handler404` |
| `config/views.py` | فقط ویو `custom_404` (صفحهٔ ۴۰۴ با breadcrumb) |
| `config/wsgi.py` / `asgi.py` | استاندارد Django (سرور پروداکشن: `gunicorn config.wsgi:application`) |

### نقشهٔ URLهای سایت

| آدرس | مقصد |
| --- | --- |
| `/` | اپ `home` (صفحهٔ اصلی) |
| `/portfolio/` | اپ `portfolio` |
| `/services/` | اپ `services` |
| `/about/` | اپ `core` (صفحهٔ درباره ما) |
| `/contact/` | اپ `contact` |
| `/blog/` | اپ `blog` |
| `/login/` و `/logout/` | ورود ادمین‌ها (قالب `templates/registration/login.html`) |
| `/who-are-you/` | 🔐 ادمین Django — عمداً از `/admin/` مبهم شده تا اسکنرها پیدا نکنند |
| `/sitemap.xml` | sitemap از `apps/core/sitemaps.py` |
| `/manifest.webmanifest` | ویو داینامیک `apps.core.views.manifest` (آیکون‌های PWA از برند انتخابی) |
| `/tinymce/` | آپلود عکس TinyMCE |
| `/public/media/...` | سرو فایل‌های آپلودی (ویو `serve` جنگو) |
| هر چیز دیگر | ۴۰۴ سفارشی (`config.views.custom_404` → `templates/404.html`) |

---

## ۴) `apps/core/` — قلب مشترک سایت (تنظیمات، برند، درباره ما)

> app_name=`core`، مونت‌شده در `/about/`. هر چیزی که «بین صفحات مشترک» است اینجاست.

| فایل | نقش |
| --- | --- |
| `models.py` | مدل‌های جدول پایین (+ متن‌های راهنمای مشترک `ICON_HELP`، `EYEBROW_HELP`، `TITLE_HELP`، `URL_HELP`) |
| `views.py` | ویو `about` (صفحهٔ درباره ما + محاسبهٔ مختصات SVG «مسیر»: `JOURNEY_DESIGN_POSITIONS` برای دقیقاً ۵ ایستگاه، وگرنه توزیع روی قوس سینوسی) و ویو `manifest` |
| `urls.py` | `""` → `about` (نام URL: `core:about`) |
| `nav.py` | 🔒 **آیتم‌های منوی بالای سایت اینجاست و ثابت است** (`NAV_ITEMS`) — طبق خواستهٔ صاحب سایت از دیتابیس/ادمین حذف شده. برای تغییر منو فقط همین لیست را ویرایش کنید |
| `context_processors.py` | `site_context` — به **همهٔ** قالب‌ها تزریق می‌کند: `settings` (SiteSettings)، `brand` (لوگو/فاوآیکون مؤثر)، `socials`، `cta` (سکشن CTA پایین صفحات)، `services_footer` (۵ خدمت برای مگامنو/فوتر)، `header_settings`، `nav_items`، `footer_groups` |
| `context_utils.py` | `crumbs()` — سازندهٔ breadcrumb همهٔ صفحات (خودش مارکرهای `[[ ]]` را حذف می‌کند) |
| `text_utils.py` | 🖋 **سینتکس `[[کلمه]]`**: ادمین داخل عنوان‌ها کلمه را در `[[ ]]` می‌گذارد تا طلایی/گرادیانی شود. `strip_highlight()` همان متن بدون مارکر را می‌دهد (برای `<title>`، متا، alt، JSON-LD) |
| `icon_utils.py` | سیستم آیکون Lucide: پارس اسپرایت لوکال، نگاشت نام‌های قدیمی (`LEGACY_ALIASES`)، ولیدیتور فیلد آیکون، ویجت آیکون‌پیکر ادمین (`IconPickerWidget`/`IconPickerForm`)، ستون پیش‌نمایش (`IconPreviewMixin`) |
| `brand_utils.py` | سیستم لوگو: پوشه‌های آمادهٔ `static/brand/option-N-*` را کشف می‌کند (۶ گزینهٔ «مدار/کسوف/دنباله‌دار/صورت فلکی/موشک/هلال») و `resolve_brand` تصمیم می‌گیرد: **فایل آپلودی ادمین همیشه بر گزینهٔ آماده مقدم است** |
| `image_utils.py` | `WebPImageMixin` — هر مدلی که `WEBP_FIELDS` دارد، تصاویر آپلودی را خودکار به WebP فشرده می‌کند (کیفیت ۸۵، حداکثر عرض ۱۶۰۰، شفافیت روی پس‌زمینهٔ تیره ترکیب می‌شود؛ فقط وقتی واقعاً کوچک‌تر شد جایگزین می‌کند) |
| `sitemaps.py` | چهار Sitemap: صفحات ثابت، نمونه‌کارها، خدمات، مقالات |
| `admin.py` | پنل ادمین مدل‌های بالا (SiteSettings با ویجت پیش‌نمایش لوگو، گروه‌های لینک فوتر، سکشن‌های درباره ما) |
| `templatetags/` | تگ‌ها/فیلترهای قالب — جدول پایین |
| `templates/core/widgets/brand_choice.html` | قالب ویجت انتخاب لوگو در ادمین |
| `management/commands/seed_about_content.py` | پرکردن محتوای پیش‌فرض صفحهٔ درباره ما (idempotent) |

### مدل‌های `core` → کجای سایت دیده می‌شوند

| مدل | نقش / محل نمایش |
| --- | --- |
| `SiteSettings` (singleton) | نام سایت، توضیحات SEO، شماره‌ها/آدرس (هدر، فوتر، CTA، صفحهٔ تماس)، متن فوتر، کارت‌های اعتماد فوتر (اینماد/ساماندهی)، **بنر مگامنوی خدمات در هدر** (`mega_title/description/cta_text`)، لوگو/فاوآیکون/آیکون iOS/تصویر OG |
| `SocialLink` | آیکون‌های شبکه‌های اجتماعی در فوتر و منوی موبایل |
| `FooterLinkGroup` + `FooterLink` | ستون‌های لینک فوتر (کاملاً از ادمین) |
| `AboutPageHero`، `AboutStory`، `AboutJourneySection` + `AboutJourneyStep`، `AboutStat` | سکشن‌های صفحهٔ «درباره ما» (`templates/core/about.html`) |

### کتابخانهٔ تگ‌های قالب (`apps/core/templatetags/`)

| فایل | تگ/فیلتر | کاربرد |
| --- | --- | --- |
| `icon_tags.py` | `{% icon "name" %}` | رندر `<svg>` آیکون Lucide از اسپرایت لوکال (`static/lucide/sprite.svg`) — بدون CDN؛ اندازه با کلاس Tailwind (`h-6 w-6`) |
| `highlight_tags.py` | `\|highlight` / `\|plain` | تبدیل `[[کلمه]]` به span طلایی / حذف مارکرها برای متن ساده |
| `nav_tags.py` | `{% nav_url value %}` | لینک‌های ادمین: هم «نام URL» (`contact:contact`) هم «مسیر» (`/blog/`) را حل می‌کند |
| `fa_digits.py` | `\|fa_digits` / `\|fa_price` | ارقام فارسی / قیمت با جداکنندهٔ هزارگان فارسی |
| `jalali_tags.py` | `\|fa_jdate` | تاریخ میلادی → شمسی («۱۲ آبان ۱۴۰۳») |
| `json_tags.py` | `\|json` | مقدار امن JSON برای بلوک‌های JSON-LD |
| `brand_tags.py` | `{% pixel_wordmark %}` | وردمارک پیکسلی «پیکسوریا» (SVG اینلاین از `static/brand/`) |
| `component_tags.py` | `{% carousel %}…{% endcarousel %}` و `\|file_exists` | پوستهٔ مشترک کاروسل‌ها + چک واقعیِ وجود فایل روی دیسک (جلوگیری از ۵۰۰ وقتی رکورد بدون فایل است) |

> تگ‌های اپ‌های دیگر: `articles_tags` (بلاگ)، `projects_tags` (پورتفولیو)، `testimonial_tags` (خدمات) — هرکدام کاروسل خودش را با کوئری داخلی می‌سازد و اگر داده خالی باشد **هیچی** چاپ نمی‌کند.

---

## ۵) `apps/home/` — صفحهٔ اصلی (سیستم سکشن‌های ترتیب‌پذیر)

> app_name=`home`، مونت‌شده در `/`. ایدهٔ اصلی: **ترتیب و فعال/غیرفعال بودن سکشن‌های صفحهٔ اصلی از مدل `HomeSection` در ادمین کنترل می‌شود** و هر کلید به یک پارشال با همان نام اشاره می‌کند.

### مدل‌ها (تقریباً همه singleton)

| مدل | سکشن متناظر |
| --- | --- |
| `HeroSection` | هیرو (عنوان + دو دکمه). آمار زیر هیرو (`hero_stats`) در ویو از دیتابیس واقعی محاسبه می‌شود: تعداد نمونه‌کارها، تعداد خدمات، «مشهد» |
| `HomeAboutSection` + `HomeAboutStat` | «درباره پیکسوریا» + شمارنده‌ها. تابلوی شیشه‌ای کنارش در ویو با ۴ کار واقعی پر می‌شود (عکس پروژه‌ها + جای خالی‌ها با کاور مقاله‌ها) |
| `ServicesSection` | سرصفحهٔ سکشن خدمات (کارت‌ها = `Service`های featured از اپ خدمات) |
| `FeaturedWorkSection` | سرصفحهٔ نمونه‌کارها (آیتم‌ها = `Portfolio`های featured؛ تعداد به مضرب ۳ گرد می‌شود تا ردیف یتیم نماند) |
| `WhySection` + `WhyFeature` | «چرا پیکسوریا» — گرید بنتو (اندازه کارت: small/wide/tall) |
| `ProcessSection` + `ProcessStep` | «فرآیند کار» — مسیر GPS |
| `TestimonialSection` | سرصفحهٔ نظرات (کارت‌ها از `ServiceTestimonial` با `show_on_home=True`) |
| `TechSection` + `TechSkill` | تکنولوژی‌ها با نوار پیشرفت |
| `StatsSection` + `StatItem` | آمار و ارقام (شمارش انیمیشنی) |
| `LatestArticlesSection` | سرصفحهٔ آخرین مقالات (کارت‌ها = `articles_carousel`) |
| `FaqSection` + `FaqItem` | سوالات متداول (+ خروجی JSON-LD نوع FAQPage برای گوگل) |
| `CTASection` | 🌐 سکشن «کال تو اکشن» — در **همهٔ صفحات** قبل از فوتر (`templates/partials/_cta.html`) |
| `HeaderSettings` | تنظیمات دکمهٔ CTA هدر (متن/لینک/نمایش) |
| `HomeSection` | 🎛 **رابطهٔ کلیدی**: هر رکورد یک سکشن است با `key` (یکی از ۱۱ کلید)، `order` و `is_active`. کلید → فایل `templates/home/sections/_<key>.html` |

### افزودن سکشن جدید به صفحهٔ اصلی — ۴ قدم

1. پارشال جدید: `templates/home/sections/_<key>.html`
2. افزودن `("key", "برچسب فارسی")` به `KEY_CHOICES` در `apps/home/models.py` (+ migration)
3. فراهم کردن context آن در `apps/home/views.py` (فقط وقتی کلید فعال است کوئری بزنید)
4. ساخت رکورد `HomeSection` در ادمین (یا اضافه‌کردن به `seed_home_content`)

---

## ۶) `apps/portfolio/` — نمونه‌کارها

| فایل | نقش |
| --- | --- |
| `models.py` | `PortfolioPageSection` (هیرو آرشیو، singleton) · `Category` (با property `filter_url`) · `Portfolio` (تصویر WebP، M2M دسته‌ها، FK اختیاری `service` به اپ خدمات + فیلد متنی قدیمی `service_type` به‌عنوان fallback، FK اختیاری `testimonial`، چالش/راهکار، تکنولوژی‌ها CSV، متای سئو، `featured`، `order`) · `ProjectStat` (آمار نتایج) · `ProjectImage` (گالری) |
| `views.py` | `portfolio_list` → همهٔ پروژه‌ها به کلاینت پاس داده می‌شوند و فیلتر دسته‌بندی در مرورگر انجام می‌شود (بدون رفرش)؛ `?category=slug` فقط دستهٔ فعال اولیه را تعیین می‌کند و اسلاگ نامعتبر ۴۰۴ نمی‌دهد. `portfolio_detail` → پروژهٔ قبلی/بعدی بر اساس `order, id` |
| `templatetags/projects_tags.py` | `{% projects_carousel exclude=… category=… service=… limit=… %}` — کاروسل پروژه‌های مرتبط |
| `admin.py` | ادمین پروژه‌ها با اینلاین آمار/گالری |
| `management/commands/seed_portfolio_content.py` | محتوای پیش‌فرض هیروی آرشیو (پروژه‌ها دست کاربرند) |
| `management/commands/compress_images.py` | تبدیل retro تصاویر قدیمی (قبل از فعال‌شدن WebP) — گزارش: `python manage.py compress_images`، اجرای واقعی: `--write` |

قالب‌ها: `templates/portfolio/list.html` و `detail.html`

---

## ۷) `apps/services/` — خدمات (بزرگ‌ترین اپ)

| فایل | نقش |
| --- | --- |
| `models.py` | (جدول پایین) |
| `views.py` | `services_list` → آرشیو خدمات + بخش «چطور انتخاب کنیم» + FAQ عمومی سایت. `services_detail` → صفحهٔ اختصاصی خدمت با همهٔ فرزندان + پرچم‌های `has_projects`/`has_articles` تا هدر کاروسل‌ها هرگز بدون کارت رندر نشود |
| `templatetags/testimonial_tags.py` | `{% testimonials_slider service=… limit=… %}` — اسلایدر نظرات (صفحهٔ اصلی = `show_on_home=True`) |
| `admin.py` | ادمین خدمت با اینلاین‌های کامل |
| `management/commands/seed_services_content.py` | محتوای پیش‌فرض صفحات اختصاصی خدمات |

### مدل‌ها → کجای سایت

| مدل | نقش |
| --- | --- |
| `Service` | خدمت: کارت در صفحهٔ اصلی/آرشیو/مگامنو + **صفحهٔ اختصاصی کامل**. فیلدهای ظاهری: `visual` (تصویرسازی CSS کارت: ماکت مرورگر/ترمینال/پالت/الماس)، `card_span` (عریض/کوچک)، `accent` (تم رنگی صفحه: gold/royal/cream/… → کلاس `svc-accent-*` در input.css)، هیرو و سئوی اختصاصی، M2M `related_services` |
| `ServiceSection` | بلوک‌های محتوای بلند صفحهٔ خدمت (متن TinyMCE + تصویر + چیدمان right/left/full). **اولین بخش فعال = «مرور کلی»** |
| `ServiceTool` / `ServiceUseCase` / `ServiceStat` / `ServiceWhyUs` / `ServiceDeliverable` / `ServiceProcess` / `ServiceFAQ` | ابزارها · صنایع · آمار · مزایا · خروجی‌ها · مراحل کار · سوالات متداولِ صفحهٔ خدمت |
| `ServicePlan` (+ `ServicePlanFeature`) | پلن‌های قیمت (دقیقاً ۳ تا؛ فقط یکی `is_featured`)؛ قیمت خالی → نمایش `price_note` («تماس بگیرید»); دکمهٔ پلن به `/contact/?service=<slug>&plan=<type>` می‌رود و فرم تماس را پیش‌پر می‌کند |
| `ServiceTestimonial` | نظرات مشتریان (متن + امتیاز + عکس گوینده) |
| `ServicesPageSection` / `ServicesHowSection` + `ServicesHowStep` | هیروی آرشیو خدمات · بخش «چطور خدمت درست را انتخاب کنیم» |

قالب‌ها: `templates/services/list.html` و `detail.html`

---

## ۸) `apps/contact/` و `apps/blog/`

### `apps/contact/` — تماس با ما (app_name=`contact`، در `/contact/`)

| فایل | نقش |
| --- | --- |
| `models.py` | سکشن‌های صفحه (`ContactPageSection`، `ContactFormSection` + `ContactFormPoint`، `ContactMapSection`، `ContactFaqSection` + `ContactFaq`) · مدل‌های انتخابی فرم (`SubjectChoice`، `ProjectTypeChoice`، `BudgetChoice`، `StartTimeChoice`) · `ContactSubmission` (پیام‌های دریافتی با وضعیت جدید/مشاهده‌شده) |
| `forms.py` | `ContactSubmissionForm` — فیلد مخفی هانی‌پات `company_website` (ربات‌ها پرش می‌کنند)؛ موضوع فقط از گزینه‌های دیتابیس؛ حداقل ۱۰ نویسه برای پیام؛ شماره اختیاری |
| `views.py` | GET → رندر صفحه؛ POST → فقط htmx: هانی‌پات → **محدودیت نرخ ۵ پیام در ساعت از روی IP** (cache جنگو) → ذخیره → پاسخ پارشال (`_contact_form.html` خطاها / `_contact_success.html` موفقیت). `_prefill` پیش‌پر کردن موضوع/متن از `?service=&plan=` — لینک خراب هرگز صفحه را نمی‌شکند |
| `admin.py` | مدیریت سکشن‌ها و مشاهدهٔ پیام‌های دریافتی |
| `management/commands/seed_contact_content.py` | محتوای پیش‌فرض صفحهٔ تماس |

قالب‌ها: `templates/contact/contact.html`، `_contact_form.html`، `_contact_success.html`

### `apps/blog/` — وبلاگ (app_name=`blog`، در `/blog/`)

| فایل | نقش |
| --- | --- |
| `models.py` | `Category` · `Tag` · `Author` · `Article` (محتوای TinyMCE؛ `reading_time` خودکار = کلمات÷۲۰۰؛ وضعیت draft/published؛ `featured` = اسلات ویژهٔ بالای آرشیو؛ متای سئو؛ M2M `related_services` برای کاروسل «مقالات این خدمت») · `BlogPageSettings` (singleton) |
| `views.py` | `article_list` → صفحه‌بندی ۹تایی + مقالهٔ ویژه. `load_articles` → دکمهٔ «بیشتر» با htmx (پارشال `load_response.html`). `article_detail` → ساخت فهرست مطالب (TOC) از `h2`ها + مقالات قبلی/بعدی هم‌دسته. `tinymce_image_upload` → آپلود عکس ادیتور (فقط staff) |
| `utils.py` | `process_content_toc` — با BeautifulSoup به `h2`ها id می‌دهد (`toc-1`, …) و لیست فهرست مطالب برمی‌گرداند |
| `templatetags/articles_tags.py` | `{% articles_carousel exclude=… category=… service=… limit=… %}` |
| `urls.py` | `""` لیست · `load/` · `tinymce-image-upload/` · `<slug>/` جزئیات |
| `management/commands/seed_blog_content.py` | تنظیمات صفحهٔ بلاگ (مقالات دست کاربرند و دست نمی‌خورد) |
| `management/commands/create_test_article.py` | ساخت یک مقالهٔ تستی کامل (تصویر تستی هم می‌سازد) |

قالب‌ها: `templates/blog/list.html`، `detail.html`، `partials/article_cards.html`، `partials/load_response.html`

---

## ۹) `templates/` — قالب‌ها

```
templates/
├── base.html              ← اسکلت مشترک همهٔ صفحات
├── 404.html               ← صفحهٔ «منظومهٔ گمشده» (handler404)
├── manifest.webmanifest   ← قالب داینامیک PWA (ویو core.views.manifest)
├── partials/              ← اجزای مشترک همهٔ صفحات
│   ├── _header.html       ← هدر شیشه‌ای + مگامنوی خدمات + منوی موبایل v3
│   ├── _footer.html       ← فوتر (برند، تماس، ستون‌های لینک، کارت‌های اعتماد، بوم «میدان زنده»)
│   ├── _cta.html          ← سکشن CTA قبل از فوتر (از CTASection)
│   ├── _brand_lockup.html / _brand_mark.html  ← لوگو (آپلودی یا پیکسلی)
│   ├── _json_logo.html / _json_telephone.html ← قطعات JSON-LD سازمان
│   └── _space_layer.html
├── components/            ← کامپوننت‌های قابل استفادهٔ مجدد
│   ├── README.md          ← 📖 مستندات کامپوننت‌ها — قبل از کار با آن‌ها بخوانید
│   ├── carousel.html      ← پوستهٔ scroll-snap + تگ {% carousel %}
│   ├── _project_card.html / _article_card.html / _testimonial_card.html  ← کارت‌های استاندارد (هر صفحهٔ جدید موظف است از همین‌ها استفاده کند)
│   ├── projects_carousel.html / articles_carousel.html / testimonials_slider.html  ← خروجی تگ‌های inclusion
│   ├── _breadcrumb.html   ← مسیر راهنما (با crumbs())
│   └── _orbit_art.html
├── home/
│   ├── index.html         ← صفحهٔ اصلی: JSON-LD سازمان/وب‌سایت + حلقهٔ سکشن‌ها بر اساس HomeSection
│   └── sections/_*.html   ← ۱۱ پارشال سکشن (هیرو، درباره، خدمات، نمونه‌کار، چرا، فرآیند، نظرات، تکنولوژی، آمار، بلاگ، FAQ)
├── portfolio/  list.html · detail.html
├── services/   list.html · detail.html
├── blog/       list.html · detail.html · partials/
├── contact/    contact.html · _contact_form.html · _contact_success.html
├── core/       about.html (+ widgets/brand_choice.html مخصوص ادمین)
├── registration/login.html   ← صفحهٔ ورود (/login/)
└── admin/login.html          ← صفحهٔ ورود ادمین
```

**نکات معماری قالب‌ها:**
- `base.html` شامل: پیش‌لودر اولین بازدید (فلگ sessionStorage)، فلگ `motion` (اگر `pixoria.js` تا ۳ ثانیه لود نشود انیمیشن‌ها لغو می‌شوند تا محتوا هرگز پنهان نماند)، متاهای SEO/OG، فاوآیکون/مانیفست از برند، نوار پیشرفت اسکرول، لودر انتقال بین صفحات، toast، و اسکریپت‌ها (`pixoria.js` به‌صورت module، `hero-field.js`، `htmx.min.js`).
- ناوبری سایت **کاملاً چندصفحه‌ای است (hx-boost حذف شده — تصمیم D15)**؛ htmx فقط در دو جا: «بیشتر» بلاگ (`blog:load`) و فرم تماس (`contact:contact`).
- قواعد کامپوننت‌ها (از `components/README.md`): هوک‌های JS فقط `data-*` (بدون id ثابت)، متن فارسی، آیکون فقط با `{% icon %}`، متن rich با `|safe` و متن ساده با `|plain`، هرگز تگ‌جینگوی واقعی داخل کامنت `{# #}` ننویسید (RecursionError می‌دهد).

---

## ۱۰) `static/` — فایل‌های استاتیک سورس

| پوشه/فایل | نقش |
| --- | --- |
| `css/tailwind.css` | ⚙️ **فایل تولیدی است — هرگز مستقیم ویرایش نکنید!** خروجی `npm run build` از `styles/input.css` |
| `css/hero.css` | استایل بوم «میدانِ زنده» (هیرو و فوتر) |
| `css/motion.css` | همهٔ انیمیشن‌های حرکتی CSS (reveal، شمارنده، …) — جایگزین GSAP |
| `css/sections.css` | بازطراحی دستنویس سکشن‌ها (کاشی‌ها، منوی موبایل، …) |
| `js/pixoria.js` | 🎛 **فایل JS اصلی سایت** (ماژول ES، ~۱۳۰۰ خط): Lenis، منوی موبایل، reveal ها با IntersectionObserver، شمارنده‌ها، اسلایدر/کاروسل‌ها، آکاردئون FAQ، فیلتر نمونه‌کار، marquee، رسم مسیر GPS فرآیند، toast، نوار پیشرفت مطالعه/TOC/کپی‌لینک بلاگ. فقط ماشه می‌زند — خودِ حرکت CSS است؛ روی دستگاه ضعیف / `prefers-reduced-motion` / لمسی همه‌چیز نرم عقب می‌نشیند |
| `js/hero-field.js` | موتور بوم دوبعدی هیرو/فوتر (شبکهٔ نقاط پیکسلی با ربایش ماوس)؛ سقف نقطه، خواب rAF خارج از دید، سازگار با htmx |
| `js/cta-animations.js` | انیمیشن‌های قدیمی Anime.js (legacy — الان بخش «چرا» با CSS کار می‌کند) |
| `js/htmx.min.js` | کتابخانهٔ htmx 1.9.10 (لوکال) |
| `js/vendor/lenis.js` · `vendor/anime.min.js` | کتابخانه‌های Lenis و Anime.js |
| `fonts/` | فونت‌های self-hosted: `font_urls.css` (@font-face ها) + woff2 های Vazirmatn (فارسی/لاتین، وزن ۳۰۰–۶۰۰) و Space Grotesk |
| `brand/` | وردمارک پیکسلی (`wordmark-full.svg`، `mark-compact.svg`) + **۶ گزینهٔ لوگوی فضایی** در `option-1-orbit` تا `option-6-crescent` (هر کدام: logo-full/mark/mono + favicon و آیکون‌های PWA) + `README.md` مستندات مفاهیم |
| `lucide/sprite.svg` | 🎯 اسپرایت آیکون‌های Lucide (v0.544) — تنها منبع آیکونِ کل سایت و ادمین |
| `admin/` | استایل/اسکریپت سفارشی ادمین: `brand_choice.css`، `icon_picker.css/js`، `lucide_icons.js` (لیست تولیدی)، به‌علاوه کپی فایل‌های پایهٔ ادمین Django |
| `demo/` | 🧪 آزمایشگاه three.js (`lab-live.html` + `three.module.js`، troika، zdog، isometric) — به صفحات سایت وصل نیست؛ فقط محیط آزمایش |

---

## ۱۱) `styles/input.css` — دیزاین‌سیستم سایت (ورودی Tailwind)

فایل ~۳۷۰۰ خطی که **تنها منبع حقیقتِ ظاهر سایت** است. با `npm run build` (یا `watch`) به `static/css/tailwind.css` کامپایل می‌شود.

- ابتدای فایل: `@theme` توکن‌های Tailwind v4 — رنگ‌ها: `ink #0a0a0c`، `ink2/ink3` (تیره‌تر)، `cream #f5f3ee`، `paper`، `coy`، طلایی سه‌گانه `gold #c9a15a` / `gold-light #e8c47a` / `gold-dark #8f6b2c`، `royal #2e63ff`؛ فونت‌ها: `Vazirmatn` (sans) و `Space Grotesk` (latin).
- ادامهٔ فایل به‌صورت بخش‌بندی‌شده با کامنت‌های `/* ---------- نام بخش ---------- */` است؛ بخش‌ها به ترتیب: glass و glass-light، کاشی نمونه‌کار، فیلتر دسته‌بندی، شفق (گوی نورانی)، کارت خدمات + ماکت مرورگر/ترمینال/پالت/الماس، «چرا»، فرآیند + مسیر GPS، کارت آمار، ابزارها، پوستر خدمات گرافیکی، اینماد فوتر، وبلاگ + اشتراک‌گذاری، FAQ، فرم لیبل شناور، نقشهٔ تماس، المان‌های شناور هیرو، تابلوی شیشه‌ای «درباره»، سامانهٔ خورشیدیِ درباره ما، هویت فضایی (T60)، **لهجهٔ رنگی صفحات خدمت `svc-accent-*` (T63)**، اتمسفر هر خدمت (T68)، کارت فهرست خدمات (T69)، nav و مگامنو، دکمه‌ها، tilt، پیش‌لودر، لودر انتقال بین صفحات، divider ها، هیرو، صفحهٔ ۴۰۴، marquee، chips، textures، اسلایدر نظرات، CTA pills، فوتر، toast، کاهش حرکت (`prefers-reduced-motion`)، و تایپوگرافی محتوای TinyMCE (انتهای فایل).

> برای تغییر رنگ/فونت/کلاس سفارشی فقط همین فایل را ویرایش کنید؛ سپس §۱۵ (تغییر استایل) را دنبال کنید.

---

## ۱۲) `public/` و `database/`

| مسیر | نقش |
| --- | --- |
| `public/static/` | خروجی `collectstatic` (نسخهٔ هش‌دار + `.gz` همهٔ فایل‌های استاتیک، شامل tinymce) — **نسخه‌پذیر نیست** (gitignore) |
| `public/media/` | فایل‌های آپلودی ادمین: `brand/`، `portfolio/`، `blog/covers/`، `blog/authors/`، `blog/content/`، `services/…`، `testimonials/`، `about/story/` — gitignore |
| `database/db.sqlite3` | دیتابیس SQLite — بکاپ‌گیری از همین فایل |

---

## ۱۳) `scripts/` — اسکریپت‌های ابزاری (به سایت سرو نمی‌شوند)

| اسکریپت | کار |
| --- | --- |
| `build_pixel_wordmark.py` | تولید وردمارک پیکسلی «پیکسوریا» و فاوآیکون‌ها از فونت Vazirmatn (با arabic_reshaper + python-bidi برای اتصال حروف) → خروجی در `static/brand/` |
| `build_brand.js` (Node) | تولید ۶ گزینهٔ لوگوی فضایی در `static/brand/option-N-*` (مسیرهای SVG واقعی از فونت‌ها؛ PNG با sharp). اجرا: `node scripts/build_brand.js` |
| `build_lucide_icons.py` | تولید لیست آیکون‌های ادمین (`static/admin/js/lucide_icons.js`) از اسپرایت + اعتبارسنجی `LEGACY_ALIASES`. **بعد از هر به‌روزرسانی اسپرایت اجرا کنید** |
| `render_check.py` | 🧪 رندر همهٔ صفحات اصلی با دیتابیس فعلی و چک کد وضعیت + نشت `[[ ]]`/CDN. اجرا: `venv\Scripts\python scripts\render_check.py` |

---

## ۱۴) نقشهٔ پنل ادمین — «فلان قسمت سایت را کجا عوض کنم؟»

ادمین: `/who-are-you/` · ورود کاربران: `/login/`

| قسمت سایت | مدل / جای تغییر |
| --- | --- |
| نام/توضیح/لوگو/فاوآیکون/شماره‌ها/آدرس سایت | `core → تنظیمات سایت (SiteSettings)` |
| آیتم‌های منوی بالا | ❌ از ادمین حذف شده — فایل `apps/core/nav.py` (`NAV_ITEMS`) |
| دکمهٔ CTA هدر | `home → تنظیمات هدر (HeaderSettings)` |
| بنر بالای مگامنوی خدمات | `SiteSettings → بخش «مگامنوی خدمات»` |
| ترتیب/نمایش سکشن‌های صفحهٔ اصلی | `home → بخش‌های صفحه اصلی (HomeSection)` |
| متن هر سکشن صفحهٔ اصلی | اپ `home` (HeroSection، WhySection، ProcessSection، …) |
| سکشن CTA پایین همهٔ صفحات | `home → CTA سکشن` |
| خدمات (کارت‌ها، صفحهٔ اختصاصی، پلن قیمت، FAQ خدمت) | اپ `services` (مدل `Service` و فرزندانش) |
| نمونه‌کارها، دسته‌ها، گالری، آمار پروژه | اپ `portfolio` |
| مقالات، دسته‌بندی/تگ/نویسنده بلاگ | اپ `blog` |
| صفحهٔ «درباره ما» | اپ `core` (AboutPageHero، AboutStory، AboutJourney، AboutStat) |
| صفحهٔ «تماس با ما» + گزینه‌های فرم + پیام‌های دریافتی | اپ `contact` |
| ستون‌های لینک فوتر | `core → ستون لینک‌های فوتر (FooterLinkGroup)` |
| شبکه‌های اجتماعی | `core → شبکه‌های اجتماعی (SocialLink)` |
| نظرات مشتریان (اسلایدر صفحهٔ اصلی) | `services → نظر مشتری` با فلگ `show_on_home` |
| کارت‌های اعتماد فوتر (اینماد/ساماندهی) | `SiteSettings → بخش «فوتر»` |
| آیکون هر رکورد | فیلد آیکون با آیکون‌پیکر (Lucide) در خود ادمین |

---

## ۱۵) جریان‌های کاری (Workflow)

### راه‌اندازی از صفر (ویندوز)
```bat
python -m venv venv
venv\Scripts\pip install -r requirements.txt
npm install
copy .env.example .env        :: مقادیر را پر کنید
venv\Scripts\python manage.py migrate
venv\Scripts\python manage.py seed_home_content
venv\Scripts\python manage.py seed_about_content
venv\Scripts\python manage.py seed_portfolio_content
venv\Scripts\python manage.py seed_services_content
venv\Scripts\python manage.py seed_blog_content
venv\Scripts\python manage.py seed_contact_content
npm run build
venv\Scripts\python manage.py collectstatic --noinput
venv\Scripts\python manage.py runserver
```
همهٔ seed ها idempotent هستند: رکوردهای موجود/ویرایش‌شده در ادمین را بازنویسی نمی‌کنند؛ اجرای دوباره‌شان بی‌خطر است.

### ⚠️ نکتهٔ حیاتی استاتیک (WhiteNoise)
در این پروژه `WHITENOISE_USE_FINDERS=False` است؛ یعنی حتی در حالت debug، استاتیک‌ها از `public/static` سرو می‌شوند، نه از پوشهٔ `static/`. بنابراین **بعد از هر تغییر در `static/` یا `styles/`**:
```bat
npm run build                                   :: فقط وقتی CSS عوض شده
venv\Scripts\python manage.py collectstatic --noinput
```
سپس صفحه را رفرش کنید. (فراموشی این مرحله = «تغییرم را نمی‌بینم!»)

### انواع تغییر → کارهای لازم

| تغییر | کارهای بعدی |
| --- | --- |
| محتوای سایت (متن، عکس، مدل‌ها) | فقط ادمین `/who-are-you/` — بدون build |
| استایل (`styles/input.css`) | `npm run build` + `collectstatic` (در حین کار: `npm run watch` + collectstatic بعد از هر ذخیره) |
| فایل CSS/JS دستی (`static/css/*.css`، `static/js/*.js`) | فقط `collectstatic` |
| مدل‌ها (`apps/*/models.py`) | `makemigrations` + `migrate` (+ ادمین را به‌روز کنید) |
| اسپرایت آیکون (`static/lucide/sprite.svg`) | `python scripts/build_lucide_icons.py` + `collectstatic` |
| لوگو/برند | ترجیحاً از ادمین (آپلود یا انتخاب گزینه)؛ بازتولید کامل: `node scripts/build_brand.js` و `python scripts/build_pixel_wordmark.py` + `collectstatic` |
| سکشن جدید صفحهٔ اصلی | ۴ قدم §۵ |
| بررسی سلامت صفحات | `venv\Scripts\python scripts\render_check.py` |

### دپلوی (Runflare)
```bash
export DJANGO_SETTINGS_MODULE=config.settings_production   # ویندوز: set
python manage.py check --deploy
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```
روی سرور `.env.production` را پر کنید (`DEBUG=False`، `ALLOWED_HOSTS`، `SECRET_KEY`، در صورت نیاز `DATABASE_URL`).

---

## ۱۶) قواعد و تله‌های مهم (Gotchas)

1. **مارکر `[[کلمه]]`**: در فیلدهای عنوان ادمین، کلمهٔ داخل `[[ ]]` طلایی می‌شود. هر جا همان متن به‌صورت ساده لازم است (title، متا، alt، JSON-LD، breadcrumb) از `|plain` استفاده می‌شود — این کار به‌صورت سیستماتیک انجام شده؛ هنگام قالب جدید رعایت کنید.
2. **Singleton ها**: اکثر مدل‌های سکشن فقط یک رکورد مجازند (خطای «فقط یک … مجاز است» + حذف دکمهٔ افزودن در ادمین).
3. **WebP خودکار**: تصاویر آپلودی همهٔ مدل‌های دارای `WEBP_FIELDS` به WebP فشرده می‌شوند؛ نیازی به فشرده‌سازی دستی نیست (تصاویر قدیمی: `compress_images --write`).
4. **آیکون‌ها فقط Lucide لوکال**: هیچ CDN ای در سایت نیست؛ نام آیکون انگلیسی است (lucide.dev/icons) و نام‌های قدیمی خودکار نگاشت می‌شوند. آیکون ناموجود = رندر هیچ (fail-soft).
5. **هیچ GSAP ای نیست**: حرکت‌ها در `motion.css`/`sections.css` است و `pixoria.js` فقط کلاس/متغیر CSS ست می‌کند (استثنا: شمارش عددی با ارقام فارسی).
6. **htmx فقط دو نقش دارد**: بارگذاری «بیشتر» بلاگ و ارسال فرم تماس؛ ناوبری عادی چندصفحه‌ای است (hx-boost حذف شده).
7. **ادمین در `/who-are-you/`** است — این مسیر را عوض نکنید مگر عمداً (در `config/urls.py`).
8. **پس از تغییر استاتیک، collectstatic فراموش نشود** (§۱۵) — رایج‌ترین دلیل «تغییر اعمال نشد».
9. **کاروسل‌ها** هرگز بدون داده رندر نمی‌شوند (تگ‌های inclusion خودشان کوئری می‌زنند)؛ برای صفحات جدید از همین تگ‌ها و کارت‌های `templates/components/` استفاده کنید.
10. **الگوهای URL از دیتابیس**: فیلدهای لینکِ ادمین هم «نام URL» (`contact:contact`) قبول می‌کنند هم مسیر مستقیم (`/blog/`) هم لنگر (`#contact`) — حل‌کننده: `{% nav_url %}`.
11. `static/css/tailwind.css` و محتویات `public/` **فایل تولیدی** هستند — سورس را ویرایش کنید، نه خروجی را.
12. `index.html` روت و پوشهٔ `static/demo/` بخشی از سایت فعال نیستند (پروتوتایپ/آزمایشگاه).

---

## ۱۷) چک‌لیست سریع «می‌خواهم X را عوض کنم»

| می‌خواهم… | برو به |
| --- | --- |
| متن هیرو / دکمه‌های صفحهٔ اصلی | ادمین → `home → هیرو سکشن` |
| رنگ یا فونت سایت | `styles/input.css` (بخش `@theme`) → build + collectstatic |
| انیمیشن یک سکشن | `static/css/motion.css` / `sections.css` (و ماشهٔ آن در `static/js/pixoria.js`) |
| یک آیکون را عوض کنم | ادمین → فیلد آیکون همان رکورد (آیکون‌پیکر) |
| منوی هدر | `apps/core/nav.py` |
| فوتر (لینک‌ها، متن، اعتماد) | ادمین → `core` (FooterLinkGroup، SiteSettings) |
| صفحهٔ خدماتِ خاص | ادمین → `services → خدمت` (+ سکشن‌ها/پلن‌ها/FAQ همان خدمت) |
| صفحهٔ یک پروژه | ادمین → `portfolio → نمونه کار` (+ آمار/گالری) |
| مقالهٔ جدید | ادمین → `blog → مقاله` |
| ۴۰۴ یا صفحهٔ ورود | `templates/404.html`، `templates/registration/login.html` |
| سئو (متا/OG/sitemap) | فیلدهای متا در هر مدل + `apps/core/sitemaps.py` + `SiteSettings.og_image` |
| فرم تماس (فیلدها/گزینه‌ها) | ادمین → `contact` (گزینه‌ها + سکشن‌ها)؛ منطق: `apps/contact/forms.py` و `views.py` |
| رفتار JS سایت | `static/js/pixoria.js` (+ `hero-field.js` برای بوم هیرو) |
| اسکریپت‌های محتوای اولیه | `apps/*/management/commands/seed_*.py` |

---
*آخرین به‌روزرسانی: ۱۴۰۵/۰۸/۰۹ — بر اساس بازرسی کامل کدبیس (Django 5.2 · Tailwind v4 · htmx 1.9.10 · Lucide v0.544).*