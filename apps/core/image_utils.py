"""فشرده‌سازی تصاویر آپلودی به WebP — با حفظ کیفیت و نسبت ابعاد.

WebP در حجمِ یکسان کیفیت بصری بهتری از JPEG/PNG دارد و پشتیبانیِ
مرورگرها از آن کامل است. این ابزار تصویر را برش نمی‌دهد و نسبتِ
ابعاد را حفظ می‌کند؛ فقط ابعاد را تا حداکثرِ مجاز پایین می‌آورد تا
فایل‌های غول‌پیکرِ اسکرین‌شات به سایت راه پیدا نکنند.
"""

from io import BytesIO
from pathlib import Path

from PIL import Image
from django.core.files.base import ContentFile

# کیفیت ۸۵ برای WebP از نظر بصری تقریباً تلفات‌ناپذیر است و حجم را
# نسبت به JPEG باکیفیتِ ۹۰ معمولاً ۲۵–۳۵٪ کمتر می‌کند.
DEFAULT_QUALITY = 85

# روشِ فشرده‌سازیِ WebP: ۰ سریع‌ترین و ۶ بهترین فشرده‌سازی است. ۴ یک
# تعادلِ معقول بین سرعت و حجم نهایی است.
DEFAULT_METHOD = 4


def _webp_name(original_name: str) -> str:
    """نام فایل را با پسوندِ webp برمی‌گرداند و حاشیه‌های اضافی را حفظ می‌کند.

    Django ممکن است برای جلوگیری از تداخلِ نام، پسوندی مثل «_XOwXvqo»
    به نام فایل اضافه کند. این پسوند باید قبل ازِ تغییرِ فرمت حفظ شود
    تا دو تصویرِ هم‌نام یکدیگر را بازنویسی نکنند.
    """
    path = Path(original_name)
    return f"{path.stem}.webp"


def compress_to_webp(
    source,
    *,
    max_width: int = 1600,
    quality: int = DEFAULT_QUALITY,
    method: int = DEFAULT_METHOD,
) -> ContentFile:
    """یک فایل تصویر می‌گیرد و نسخهٔ WebPِ فشردهٔ آن را برمی‌گرداند.

    source:     فایل بازشده (File-like) — مثلاً field.file
    max_width:  حداکثر پهنای مجاز؛ تصویرِ پهن‌تر با حفظ نسبت کوچک می‌شود.
    quality:    کیفیت WebP (۰ تا ۱۰۰).
    method:     میزان تلاشِ انکودر (۰ تا ۶).

    خروجی یک ContentFile با نامِ webp است که می‌توان مستقیماً در فیلد
    ذخیره کرد. تصویرِ شفاف (PNG با کانال آلفا) روی پس‌زمینهٔ تیرهٔ
    سایت قرار می‌گیرد، بنابراین آلفا روی مشکیِ ساده ترکیب می‌شود.
    """
    image = Image.open(source)
    image.load()

    if image.mode in ("RGBA", "LA", "P"):
        # لوگوها و گرافیک‌ها معمولاً شفاف‌اند؛ روی پس‌زمینهٔ تیرهٔ سایت
        # (نه سفید) ترکیب می‌شوند تا حاشیهٔ زشتِ روشن دورشان نماند.
        background = Image.new("RGB", image.size, (10, 10, 12))
        image = image.convert("RGBA")
        background.paste(image, mask=image.split()[-1])
        image = background
    elif image.mode != "RGB":
        image = image.convert("RGB")

    if image.width > max_width:
        ratio = max_width / image.width
        new_size = (max_width, round(image.height * ratio))
        image = image.resize(new_size, Image.LANCZOS)

    buffer = BytesIO()
    image.save(buffer, format="WEBP", quality=quality, method=method)
    buffer.seek(0)

    original_name = getattr(source, "name", "") or "image"
    return ContentFile(buffer.getvalue(), name=_webp_name(original_name))


def compress_to_webp_if_smaller(
    source, *, max_width: int = 1600, quality: int = DEFAULT_QUALITY,
    method: int = DEFAULT_METHOD, min_gain: float = 0.02
):
    """تصویر را فقط وقتی به WebP تبدیل می‌کند که واقعاً کوچک‌تر شود.

    برخلافِ compress_to_webp (که همیشه تبدیل می‌کند)، اگر نسخهٔ WebP
    حداقل به اندازهٔ min_gain کوچک‌تر نشد، None برمی‌گرداند تا فایلِ
    اصلی دست‌نخورده باقی بماند. این برای تصاویری است که از قبل فشرده
    شده‌اند (مثلاً JPEGِ باکیفیتِ پایین) که تبدیلِ دوباره فقط حجم را
    زیاد و کیفیت را کم می‌کند.

    بازگشت: ContentFileِ WebP، یا None اگر تبدیل سودی نداشت.
    """
    original_size = getattr(source, "size", None)
    compressed = compress_to_webp(source, max_width=max_width, quality=quality, method=method)
    if original_size is None:
        return compressed
    new_size = compressed.size
    if new_size >= original_size * (1 - min_gain):
        return None
    return compressed
