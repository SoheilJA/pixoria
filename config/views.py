from django.shortcuts import render

from apps.core.context_utils import crumbs


def custom_404(request, exception):
    return render(
        request,
        '404.html',
        {"crumbs": crumbs(("خانه", "home:home"), ("خطای ۴۰۴", None))},
        status=404,
    )
