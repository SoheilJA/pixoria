"""Plain-text helpers for admin-authored strings.

Titles and headings may carry ``[[…]]`` highlight markers: the template filter
``apps.core.templatetags.highlight_tags.highlight`` turns them into a gold
gradient span. Anywhere the *same* text is consumed as plain text — ``<title>``,
meta/OG tags, breadcrumbs, ``alt``/``aria-label``, JSON-LD and share URLs — the
markers must be removed first, otherwise the raw brackets leak to the visitor.

Both the ``highlight`` and the ``plain`` template filters build on this module,
so the marker syntax is defined exactly once.
"""

import re

#: ``[[کلمه]]`` — the marker admins type in the admin panel.
MARKER_RE = re.compile(r"\[\[(.+?)\]\]")


def strip_highlight(value):
    """Return ``value`` without ``[[…]]`` markers (the inner text is kept).

    Safe to call on marker-free text (including ``None``) — it is a no-op then.
    """
    if not value:
        return ""
    return MARKER_RE.sub(r"\1", str(value))
