"""تنظیماتِ سرورِ آنلاین (پروداکشن).

از `config.settings` ارث می‌برد و فقط فایلِ `.env.production` را به جای
`.env` بارگذاری می‌کند (تنظیمِ `DJANGO_SETTINGS_MODULE` در همان ماژولِ
پایه انتخاب می‌شود). بقیهٔ تفاوت‌های پروداکشن در همین فایل اعمال می‌شوند.

استفاده روی سرور:
    export DJANGO_SETTINGS_MODULE=config.settings_production
    python manage.py check --deploy
    python manage.py migrate
    python manage.py collectstatic --noinput
    gunicorn config.wsgi:application  (با DJANGO_SETTINGS_MODULE بالا)
"""

from .settings import *  # noqa: F401,F403

# DEBUG باید False باشد — در غیر این صورت کد و متغیرها نشت می‌کنند.
# این مقدار از `.env.production` هم خوانده می‌شود ولی اینجا به عنوان
# یک تورِ ایمنیِ آخری هم بازنویسی می‌شود.
DEBUG = False

# نشست‌ها و CSRF باید روی HTTPS کار کنند.
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # یک سال
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# هدرهای امنیتی پایه.
X_FRAME_OPTIONS = "DENY"
