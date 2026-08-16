# ساختار detail.html - مقاله بلاگ

## نمای کلی

فایل `detail.html` اکنون به صورت **modular** و **component-based** است. هر بخش در یک فایل جداگانه (partial) قرار دارد که خوانایی و نگهداری را بهبود می‌دهد.

---

## بخش‌های اصلی

### 1. **detail_hero.html** - بخش بالای صفحه

شامل:

- **Breadcrumb Navigation** - مسیر پیمایش (خانه ← بلاگ ← دسته‌بندی)
- **Category & Tags** - دسته‌بندی و تگ‌های مقاله
- **Article Title** - عنوان اصلی
- **Metadata Bar** - نویسنده، تاریخ انتشار، زمان مطالعه، آپدیت

### 2. **detail_cover.html** - تصویر کاور

- تصویر شاخص مقاله
- با `loading="eager"` برای بارگذاری فوری

### 3. **detail_body.html** - محتوای اصلی

شامل:

- **Lead Paragraph** - خلاصه مقاله (excerpt)
- **Main Content** - محتوای HTML از TinyMCE
- **Social Share Buttons** - دکمه‌های اشتراک‌گذاری (Twitter, LinkedIn, Telegram, Copy Link)

### 4. **Sidebar Sections** - نوار جانبی

#### a) **sidebar_toc.html** - فهرست مطالب

- لیست تمام `<h2>` های مقاله
- هر آیتم به section مرتبط لینک می‌دهد

#### b) **sidebar_author.html** - کارت نویسنده

- تصویر نویسنده
- نام، عنوان شغلی، بیوگرافی

#### c) **sidebar_related.html** - مقالات مرتبط

- 3 مقاله از همان دسته‌بندی
- کارت کوچک با تصویر و اطلاعات

#### d) **sidebar_cta.html** - Call-to-Action

- پیام مشاوره رایگان
- دکمه لینک شده به صفحه تماس

### 5. **detail_related_section.html** - بخش مقالات مرتبط

- Grid کامل مقالات مرتبط (3 ستون)
- نمایش بیشتر از sidebar

### 6. **detail_post_nav.html** - ناوبری مقالات

- Link به مقاله قبلی و بعدی
- **فقط در همان دسته‌بندی**

### 7. **detail_cta.html** - Call-to-Action نهایی

- بخش تشویق برای تماس و درخواست پروژه

---

## جریان داده‌ها (Context)

فایل `views.py` سیاق (context) زیر را فراهم می‌کند:

```python
{
    'article': Article,           # مقاله فعلی
    'content_html': str,          # محتوای HTML (پردازش‌شده)
    'toc': list,                  # فهرست مطالب [{id, text, number}]
    'related_articles': list,     # 3 مقاله مرتبط
    'prev_article': Article,      # مقاله قبلی در دسته‌بندی
    'next_article': Article,      # مقاله بعدی در دسته‌بندی
}
```

---

## ویژگی‌های Django Template

### Dynamic Rendering

- `{{ article.field }}` - نمایش داده‌های مدل
- `{% for item in list %}` - حلقه‌های داینامیک
- `{% if condition %}` - شرط‌های پویا
- `{% url 'name' param %}` - تولید URL داینامیک

### Filters

- `|date:"d F Y"` - فرمت‌بندی تاریخ
- `|safe` - نمایش HTML بدون escape
- `|urlencode` - کدگذاری URL

### Comments

- `{% comment %}...{% endcomment %}` - توضیحات برای توسعه‌دهندگان

---

## JavaScript Enhancements

### 1. **Table of Contents Active Link**

- Intersection Observer برای تشخیص section فعلی
- خودکار highlight کردن TOC item

### 2. **Copy Link Button**

- کپی URL صفحه به clipboard
- پیام بازخورد "✓ کپی شد" برای 2 ثانیه

---

## مدل‌های مرتبط

### Article

```python
title              # عنوان مقاله
slug               # اسلاگ (برای URL)
category           # دسته‌بندی (FK)
tags               # برچسب‌ها (M2M)
author             # نویسنده (FK)
cover_image        # تصویر کاور
excerpt            # خلاصه
content            # محتوای HTML
reading_time       # زمان مطالعه (خودکار محاسبه)
published_at       # تاریخ انتشار
updated_at         # آخرین ویرایش
is_updated()       # متد: آپدیت شده؟
```

### Author

```python
name               # نام نویسنده
role               # عنوان شغلی
avatar             # تصویر پروفایل
bio                # بیوگرافی
initial()          # متد: اولین حرف نام
```

---

## فایل‌های CSS

**`static/css/blog.css`** شامل:

- `.post-hero` - سبک بخش بالای صفحه
- `.post-cover` - سبک تصویر کاور
- `.post-body` - سبک محتوای اصلی
- `.post-sidebar` - سبک نوار جانبی
- `.post-nav` - سبک ناوبری
- `.related-*` - سبک‌های مقالات مرتبط
- Responsive breakpoints برای موبایل/تبلت

---

## بهینه‌سازی‌های اعمال‌شده

✅ **Modular Structure** - هر بخش در فایل جداگانه
✅ **Better Maintainability** - آپدیت کردن بخش‌ها آسان‌تر
✅ **SEO-Friendly** - aria labels, semantic HTML
✅ **Performance** - `loading="lazy"` برای تصاویر
✅ **Accessibility** - title, aria-label برای دکمه‌ها
✅ **Same Category Navigation** - مقالات قبلی/بعدی از دسته‌بندی
✅ **Better Comments** - توضیحات برای توسعه‌دهندگان
