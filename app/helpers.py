# app/helpers.py
import requests
from flask import current_app, request
from app.models.setting import Setting


def verify_recaptcha(recaptcha_response):
    """Verify reCAPTCHA response"""

    # اگه reCAPTCHA غیرفعال باشه، همیشه True برمی‌گردونه
    if not Setting.is_recaptcha_enabled():
        return True

    # اگه کلیدها تنظیم نشده باشن
    if not current_app.config.get("RECAPTCHA_SECRET_KEY"):
        current_app.logger.warning(
            "reCAPTCHA is enabled but SECRET_KEY is not configured"
        )
        return True  # در حالت dev اجازه بده

    if not recaptcha_response:
        return False

    try:
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": current_app.config["RECAPTCHA_SECRET_KEY"],
                "response": recaptcha_response,
                "remoteip": request.remote_addr,
            },
            timeout=5,
        )
        result = response.json()
        return result.get("success", False)
    except Exception as e:
        current_app.logger.error(f"reCAPTCHA verification failed: {str(e)}")
        return False  # در صورت خطا، امنیت رو حفظ می‌کنیم
