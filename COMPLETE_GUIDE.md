# 📚 راهنمای کامل ایجاد مقاله تستی

## 🎯 مقصد

ایجاد یک مقاله تستی کامل برای تست کردن تمپلیت `detail.html` و تمام بخش‌های آن.

---

## 🚀 روش اجرا

### روش 1️⃣: استفاده از Django Shell (بدون نیاز به PIL)

```bash
cd /path/to/pixoria
python manage.py shell < create_test_simple.py
```

**مزایا:**

- ✅ ساده‌ترین روش
- ✅ بدون نیاز به Pillow
- ✅ سریع و مستقیم

---

### روش 2️⃣: استفاده از Admin Panel

1. وارد admin شوید: `http://localhost:8000/admin/`
2. برای ایجاد Author:
   - **Name**: نازنین نادری
   - **Role**: توسعه‌دهنده بک‌اند · بنیان‌گذار
   - **Bio**: متخصص در توسعه وب...
3. برای ایجاد Category:
   - **Title**: تکنولوژی
   - **Slug**: تکنولوژی
4. برای ایجاد Tags:
   - Django
   - Python
   - وب‌سایت
   - بک‌اند
   - API
5. برای ایجاد Article:
   - **Title**: Django: بهترین انتخاب...
   - **Slug**: django-بهترین-انتخاب-برای-پروژه‌های-بزرگ
   - **Category**: تکنولوژی
   - **Author**: نازنین نادری
   - **Excerpt**: (خلاصه مقاله)
   - **Content**: (محتوای کامل)
   - **Status**: منتشر شده
   - **Published At**: 5 روز پیش
   - **Meta Title**: Django: بهترین انتخاب...
   - **Meta Description**: بررسی کامل Django...

---

## 📋 مشخصات مقاله

### عنوان و معلومات پایه

- **Title**: Django: بهترین انتخاب برای پروژه‌های بزرگ و مقیاس‌پذیر
- **Slug**: django-بهترین-انتخاب-برای-پروژه‌های-بزرگ
- **Status**: منتشر شده (published)
- **Published Date**: 5 روز پیش

### نویسنده

- **Name**: نازنین نادری
- **Role**: توسعه‌دهنده بک‌اند · بنیان‌گذار
- **Bio**: متخصص در توسعه وب با Django و Python...

### محتوا

```
Total Sections: 6 (h2)
- مقدمه‌ای بر Django
- ویژگی‌های برتر Django
- معماری MTV
- مقیاس‌پذیری و کارایی
- اکوسیستم و Packages
- نتیجه‌گیری

Code Blocks: 3
Callout Boxes: 2 (including 1 warning)
Stats Box: 1
Lists: 2 (ul)
Paragraphs: 15+
Total Characters: ~4500+
```

### Tags

1. Django
2. Python
3. وب‌سایت
4. بک‌اند
5. API

### SEO

- **Meta Title**: Django: بهترین انتخاب برای پروژه‌های بزرگ و مقیاس‌پذیر
- **Meta Description**: بررسی کامل Django و دلایل استفاده از این فریم‌ورک...
- **Excerpt**: خلاصه مقاله برای لیست مقالات

---

## ✨ بخش‌های مقاله

### 1️⃣ Hero Section

```django
{% include 'blog/partials/detail_hero.html' %}
```

- Breadcrumb navigation
- Category & Tags
- Article title
- Metadata bar (author, date, reading time, update info)

### 2️⃣ Cover Image

```django
{% include 'blog/partials/detail_cover.html' %}
```

### 3️⃣ Main Layout

```django
<div class="post-layout">
  {% include 'blog/partials/detail_body.html' %}
  <aside class="post-sidebar">
    {% include 'blog/partials/sidebar_toc.html' %}
    {% include 'blog/partials/sidebar_author.html' %}
    {% include 'blog/partials/sidebar_related.html' %}
    {% include 'blog/partials/sidebar_cta.html' %}
  </aside>
</div>
```

### 4️⃣ Body Section

- Lead paragraph (excerpt)
- Main content (HTML)
- Social share buttons (Twitter, LinkedIn, Telegram, Copy Link)

### 5️⃣ Sidebar Blocks

- **Table of Contents**: تمام h2 ها به صورت interactive
- **Author Card**: نویسنده + تصویر + نقش + بیوگرافی
- **Related Articles**: 3 مقاله مرتبط از دسته‌بندی
- **CTA Box**: فراخوان برای مشاوره رایگان

### 6️⃣ Related Posts Section

```django
{% include 'blog/partials/detail_related_section.html' %}
```

- Grid layout (3 columns)
- Related articles

### 7️⃣ Navigation

```django
{% include 'blog/partials/detail_post_nav.html' %}
```

- Previous article (از دسته‌بندی)
- Next article (از دسته‌بندی)

### 8️⃣ Final CTA

```django
{% include 'blog/partials/detail_cta.html' %}
```

- فراخوان نهایی برای شروع پروژه

---

## 🌐 دسترسی به مقاله

پس از اجرای script:

```
http://localhost:8000/blog/django-بهترین-انتخاب-برای-پروژه‌های-بزرگ/
```

---

## 📊 چیزهایی برای تست کردن

### ✅ Functionality Tests

- [ ] صفحه مقاله بارگذاری شود
- [ ] تمام بخش‌ها نمایش داده شود
- [ ] لینک‌های شامل فعال باشند
- [ ] دکمه اشتراک‌گذاری کار کنند
- [ ] دکمه کپی لینک کار کند
- [ ] ناوبری مقاله قبلی/بعدی کار کند

### 📱 Responsive Tests

- [ ] صفحه در موبایل صحیح نمایش داده شود
- [ ] sidebar در موبایل collapse شود
- [ ] تصاویر responsive باشند

### ♿ Accessibility Tests

- [ ] تمام دکمه‌ها accessible باشند
- [ ] aria-labels صحیح باشند
- [ ] Headings sequence درست باشند

### ⚡ Performance Tests

- [ ] صفحه سریع بارگذاری شود
- [ ] تصاویر lazy-loaded باشند
- [ ] Database queries optimized باشند

---

## 📝 فایل‌های مربوطه

```
pixoria/
├── create_test_simple.py              ← Script اصلی
├── create_test_data_direct.py         ← نسخه دیگر (PIL required)
├── CREATE_TEST_ARTICLE.md             ← این فایل
├── BLOG_STRUCTURE.md                  ← ساختار template
├── apps/blog/
│   ├── models.py                      ← مدل‌های Django
│   ├── views.py                       ← views
│   ├── admin.py                       ← admin panel
│   └── management/
│       └── commands/
│           └── create_test_article.py ← Management command
└── templates/blog/
    ├── detail.html                    ← صفحه اصلی
    └── partials/
        ├── detail_hero.html
        ├── detail_cover.html
        ├── detail_body.html
        ├── sidebar_toc.html
        ├── sidebar_author.html
        ├── sidebar_related.html
        ├── sidebar_cta.html
        ├── detail_related_section.html
        ├── detail_post_nav.html
        └── detail_cta.html
```

---

## 🎉 نتیجه

پس از اجرای script، شما یک مقاله کامل درخواهید داشت که:

✅ تمام بخش‌های template استفاده می‌کند  
✅ محتوای غنی و متنوع دارد  
✅ برای تست‌کردن مناسب است  
✅ SEO-friendly است  
✅ Fully responsive است

Happy Testing! 🚀
