# 📝 ایجاد مقاله تستی برای بلاگ

## روش‌های موجود

### روش 1: استفاده از Management Command (توصیه شده)

```bash
python manage.py create_test_article
```

### روش 2: استفاده از Direct Python Script

```bash
python manage.py shell < create_test_data_direct.py
```

### روش 3: اجرا درون Django Shell

```bash
python manage.py shell
```

سپس در shell، کد زیر را اجرا کنید:

```python
exec(open('create_test_data_direct.py').read())
```

---

## چه چیزی اضافه می‌شود؟

### 📂 Category

- **Title**: تکنولوژی
- **Slug**: تکنولوژی

### 🏷️ Tags

- Django
- Python
- وب‌سایت
- بک‌اند
- API

### ✍️ Author

- **Name**: نازنین نادری
- **Role**: توسعه‌دهنده بک‌اند · بنیان‌گذار
- **Bio**: متخصص در توسعه وب با Django و Python...
- **Avatar**: تصویر تستی

### 📄 Article

- **Title**: Django: بهترین انتخاب برای پروژه‌های بزرگ و مقیاس‌پذیر
- **Slug**: django-بهترین-انتخاب-برای-پروژه‌های-بزرگ
- **Status**: منتشر شده
- **Published Date**: 5 روز پیش
- **Content**: مقاله کامل با 6 section و کد‌های نمونه
- **Cover Image**: تصویر تستی (1600x900)
- **Meta Title**: برای SEO
- **Meta Description**: برای SEO

---

## ساختار محتوای مقاله

مقاله شامل بخش‌های زیر است:

1. **مقدمه‌ای بر Django** - معرفی کلی
2. **ویژگی‌های برتر Django** - ORM، Admin، Auth، Forms
3. **معماری MTV** - توضیح الگوی معماری
4. **Stats Box** - نمایش اطلاعات آماری
5. **مقیاس‌پذیری و کارایی** - بهینه‌سازی queries
6. **اکوسیستم و Packages** - معرفی کتابخانه‌های تکمیلی
7. **نتیجه‌گیری** - خلاصه

---

## مشخصات محتوا

- **Total Characters**: ~4500+
- **Headings (H2)**: 6 عدد
- **Code Blocks**: 3 عدد
- **Lists**: 2 عدد
- **Callout Boxes**: 2 عدد
- **Stats Row**: 1 عدد
- **Paragraphs**: 15+ عدد

---

## آدرس دسترسی

پس از اجرای script، می‌توانید مقاله را از طریق URL زیر ببینید:

```
http://localhost:8000/blog/django-بهترین-انتخاب-برای-پروژه‌های-بزرگ/
```

---

## توجه‌های مهم

- ⚠️ اگر مقاله قبلاً وجود داشت، دوباره ایجاد نخواهد شد
- 📸 تصاویر تستی به صورت خودکار ایجاد می‌شوند (نیاز به Pillow)
- 🔄 استفاده از `get_or_create` برای جلوگیری از duplicate‌ها

---

## نیازمندی‌ها

```bash
pip install Pillow  # برای ایجاد تصاویر تستی
```

تمام وابستگی‌های دیگر قبلاً در `requirements.txt` وجود دارند.
