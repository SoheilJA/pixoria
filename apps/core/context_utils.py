"""Shared helpers for building template context.

`crumbs` builds the breadcrumb trail rendered by
`templates/components/_breadcrumb.html` (shared by every v2 page hero). Pass
ancestor pages oldest-first; the last item is rendered as the current page.
Labels are Persian.

Labels run through :func:`apps.core.text_utils.strip_highlight`, so passing a
model title (``article.title``) is safe even when the admin wrapped a word in
``[[…]]`` highlight markers — a breadcrumb is plain text and must never show
the raw brackets.

Usage in a view::

    from apps.core.context_utils import crumbs

    context = {
        "crumbs": crumbs(
            ("خانه", "home:home"),
            ("بلاگ", "blog:list"),
            (article.title, None),
        ),
    }
"""

from django.urls import reverse

from apps.core.text_utils import strip_highlight

LABEL_ONLY = 0
NAMED_URL = 1


def crumbs(*items):
    """Build a breadcrumb list for components/breadcrumb.html.

    Each item is either a plain string (label of the current page) or a
    ``(label, url_name)`` tuple whose url is resolved with reverse().
    A tuple with ``url_name=None`` also marks the current page, so a trail
    can be built uniformly: ``("بلاگ", "blog:list"), (article.title, None)``.
    """
    trail = []
    for item in items:
        if isinstance(item, str):
            trail.append({"label": strip_highlight(item)})
        else:
            label, url_name = item
            entry = {"label": strip_highlight(label)}
            if url_name is not None:
                entry["url"] = reverse(url_name)
            trail.append(entry)
    return trail
