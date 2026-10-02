"""Convert ServiceWhyUs.icon emoji values to Lucide icon names."""

from django.db import migrations

# Emoji previously allowed by the CharField → their Lucide equivalents.
EMOJI_TO_LUCIDE = {
    "⚡": "zap",
    "📱": "smartphone",
    "💻": "laptop",
    "🖥️": "monitor",
    "🎨": "palette",
    "🖌️": "paintbrush",
    "✏️": "pencil",
    "🔒": "shield-check",
    "🛡️": "shield",
    "🔐": "key-round",
    "💡": "lightbulb",
    "🎯": "target",
    "🚀": "rocket",
    "✨": "sparkles",
    "⭐": "star",
    "🌟": "star",
    "📈": "trending-up",
    "📊": "bar-chart-3",
    "💰": "wallet",
    "🛠️": "wrench",
    "⚙️": "settings",
    "🔧": "wrench",
    "🌐": "globe",
    "🔗": "link",
    "💬": "message-circle",
    "📞": "phone",
    "📧": "mail",
    "✅": "circle-check-big",
    "❌": "x",
    "❤️": "heart",
    "👍": "thumbs-up",
    "🏆": "trophy",
    "📋": "clipboard-list",
    "🔍": "search",
    "🎥": "video",
    "📸": "camera",
    "🎵": "music",
}

FALLBACK = "sparkles"


def is_emoji(value):
    """True when the stored value is a symbol/emoji rather than an ascii icon name."""
    return any(ord(ch) > 0x2000 for ch in value)


def forwards(apps, schema_editor):
    ServiceWhyUs = apps.get_model("services", "ServiceWhyUs")
    for row in ServiceWhyUs.objects.all():
        value = (row.icon or "").strip()
        if not value:
            new = FALLBACK
        elif is_emoji(value):
            new = EMOJI_TO_LUCIDE.get(value, FALLBACK)
        else:
            continue  # already a lucide name (or a custom name) — leave untouched
        if new != row.icon:
            row.icon = new
            row.save(update_fields=["icon"])


def backwards(apps, schema_editor):
    """Not reversible to emoji — restore a neutral placeholder icon name."""
    ServiceWhyUs = apps.get_model("services", "ServiceWhyUs")
    ServiceWhyUs.objects.all().update(icon="sparkles")


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0003_alter_servicewhyus_icon"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
