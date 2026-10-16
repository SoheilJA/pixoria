"""Brand preset discovery + resolution (T58).

``scripts/build_brand.js`` (T57) generates the logo option set under
``static/brand/option-N-<name>/`` — six space-themed concepts, each a folder
holding ``logo-full.svg``, ``logo-mark.svg``, the mono variants, ``favicon.svg``
and the PNG sizes. This module

* discovers those folders (so a new ``option-7-*`` folder is picked up with no
  code change),
* exposes them as model choices for ``SiteSettings.logo_choice`` /
  ``favicon_choice``,
* resolves the *effective* brand assets for a settings row, where an uploaded
  file always wins over a preset, and
* ships ``BrandChoiceWidget``, the admin radio with an image preview per option.

Resolution never raises: with no ``SiteSettings`` row, no preset folder or a
stale choice it falls back to the first option it can find, and finally to empty
strings (templates are written to skip empty brand URLs).
"""

from functools import lru_cache
from pathlib import Path

from django import forms
from django.conf import settings as django_settings
from django.templatetags.static import static

OPTION_PREFIX = "option-"

# Persian concept names keyed by folder id. ``scripts/build_brand.js`` writes
# the same names into ``static/brand/README.md``; a folder missing from this map
# falls back to the tail of its slug.
OPTION_NAMES = {
    "option-1-orbit": "مدار",
    "option-2-eclipse": "کسوف",
    "option-3-comet": "دنباله‌دار",
    "option-4-constellation": "صورت فلکی",
    "option-5-rocket": "موشک",
    "option-6-crescent": "هلال",
}

# Asset key → filename inside an option folder.
ASSETS = {
    "logo_full": "logo-full.svg",
    "mark": "logo-mark.svg",
    "mono_light": "logo-mono-light.svg",
    "mono_dark": "logo-mono-dark.svg",
    "favicon_svg": "favicon.svg",
    "favicon_16": "favicon-16.png",
    "favicon_32": "favicon-32.png",
    "apple_touch": "apple-touch-icon.png",
    "icon_192": "icon-192.png",
    "icon_512": "icon-512.png",
}

# The two files without which a folder is not a usable option.
_REQUIRED_FILES = ("logo-mark.svg", "favicon.svg", "icon-512.png")


@lru_cache(maxsize=1)
def brand_options():
    """Tuple of ``(folder_id, persian_label)`` for every built brand option.

    Sorted by folder name, so ``option-1-orbit`` is always first and therefore
    the default. Empty (not ``None``) when nothing is built yet.
    """
    found = {}
    for base in django_settings.STATICFILES_DIRS:
        root = Path(base) / "brand"
        if not root.is_dir():
            continue
        for path in root.iterdir():
            if (
                path.is_dir()
                and path.name.startswith(OPTION_PREFIX)
                and all((path / name).is_file() for name in _REQUIRED_FILES)
            ):
                found.setdefault(path.name, OPTION_NAMES.get(path.name))
    return tuple(
        (name, label or name.split("-", 2)[-1])
        for name, label in sorted(found.items())
    )


def default_brand_option():
    """The first option id, or ``""`` when no option is built."""
    options = brand_options()
    return options[0][0] if options else ""


def brand_choices():
    """Model choices: ``(folder_id, "نام فارسی (option-n-slug)")``."""
    return [(oid, f"{label} ({oid})") for oid, label in brand_options()]


def _effective_choice(choice):
    """The choice that actually resolves: the stored one, or the first option.

    A stale ``choice`` (an option folder deleted after the admin picked it, or a
    typo) must never leak into the rendered ``id``/URLs.
    """
    if choice in dict(brand_options()):
        return choice
    return default_brand_option()


def _preset_urls(choice):
    """Static URLs of every asset of ``choice`` (empty dict when none is built)."""
    choice = _effective_choice(choice)
    if not choice:
        return {}
    return {
        key: static(f"brand/{choice}/{name}")
        for key, name in ASSETS.items()
    }


def _abs(request, url):
    """Absolute URL (OG images and JSON-LD need one); ``""`` for an empty one."""
    if not url:
        return ""
    if url.startswith(("http://", "https://")):
        return url
    if request is None:
        return url
    return request.build_absolute_uri(url)


def resolve_brand(site_settings, *, request=None):
    """The effective brand assets for the templates.

    Priority per the task: an uploaded file wins over the chosen preset, and a
    missing/invalid choice falls back to the first option. ``site_settings`` may
    be ``None`` (empty database) — the presets still resolve.

    Returns a dict with, among others:

    * ``id`` / ``name`` — the effective preset (``""`` when none is built),
    * ``logo_full`` — the mark + wordmark lockup (upload or preset),
    * ``mark`` / ``mono_light`` / ``mono_dark`` — the mark alone,
    * ``favicon_svg`` / ``favicon_32`` / ``icon_192`` / ``apple_touch``,
    * ``og_image`` / ``schema_logo`` — always absolute, for meta tags + JSON-LD,
    * ``is_upload`` — a custom logo was uploaded (the wordmark is then the
      file's own business, so templates drop the CSS wordmark).
    """
    upload_logo = bool(site_settings and site_settings.logo)
    logo_choice = getattr(site_settings, "logo_choice", "") or ""
    favicon_choice = getattr(site_settings, "favicon_choice", "") or ""

    logo_preset = _preset_urls(logo_choice)
    # یک favicon_choice خالی به گزینهٔ لوگو می‌چسبد (نه به گزینهٔ اول) — تا
    # ادمینی که فقط لوگو را عوض می‌کند آیکون‌های هم‌نام بگیرد. انتخابِ نامعتبر
    # (مثلاً پوشهٔ حذف‌شده) داخلِ _preset_urls به گزینهٔ اول برمی‌گردد.
    icon_preset = _preset_urls(favicon_choice) if favicon_choice else logo_preset

    logo_full = site_settings.logo.url if upload_logo else logo_preset.get("logo_full", "")
    favicon_svg = site_settings.favicon.url if (site_settings and site_settings.favicon) else icon_preset.get("favicon_svg", "")
    apple_touch = (
        site_settings.apple_touch_icon.url
        if site_settings and site_settings.apple_touch_icon
        else icon_preset.get("apple_touch", "")
    )
    og_upload = site_settings.og_image.url if (site_settings and site_settings.og_image) else ""

    return {
        "id": _effective_choice(logo_choice),
        "name": dict(brand_options()).get(_effective_choice(logo_choice), ""),
        "is_upload": upload_logo,
        "logo_full": logo_full,
        "mark": logo_preset.get("mark", ""),
        "mono_light": logo_preset.get("mono_light", ""),
        "mono_dark": logo_preset.get("mono_dark", ""),
        "favicon_svg": favicon_svg,
        "favicon_16": icon_preset.get("favicon_16", ""),
        "favicon_32": icon_preset.get("favicon_32", ""),
        "icon_192": icon_preset.get("icon_192", ""),
        "icon_512": icon_preset.get("icon_512", ""),
        "apple_touch": apple_touch,
        # Meta tags and structured data need absolute URLs.
        "og_image": _abs(request, og_upload or icon_preset.get("icon_512", "")),
        "schema_logo": _abs(request, icon_preset.get("icon_512", "")),
    }


class BrandChoiceWidget(forms.RadioSelect):
    """Radio of the built brand options, each with its mark as a preview.

    Renders ``templates/core/widgets/brand_choice.html``; the per-option image
    URL is attached in :meth:`create_option` so the template stays declarative.
    """

    template_name = "core/widgets/brand_choice.html"

    class Media:
        css = {"all": ("admin/css/brand_choice.css",)}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        option["src"] = static(f"brand/{value}/logo-mark.svg") if value else ""
        option["src_full"] = static(f"brand/{value}/logo-full.svg") if value else ""
        return option
