from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Article, Category

PAGE_SIZE = 9


def _get_articles(category_slug):
    qs = Article.objects.filter(status="published", published_at__lte=timezone.now())
    if category_slug and category_slug != "all":
        qs = qs.filter(category__slug=category_slug)
    return qs.select_related("category").order_by("-published_at")


def article_list(request):
    qs = _get_articles("all")
    paginator = Paginator(qs, PAGE_SIZE)
    page_obj = paginator.get_page(1)
    context = {
        "categories": Category.objects.all(),
        "articles": page_obj.object_list,
        "has_next": page_obj.has_next(),
        "next_page": 2,
        "current_category": "all",
    }
    return render(request, "blog/list.html", context)


def load_articles(request):
    category_slug = request.GET.get("category", "all")
    page_number = request.GET.get("page", 1)

    qs = _get_articles(category_slug)
    paginator = Paginator(qs, PAGE_SIZE)
    page_obj = paginator.get_page(page_number)

    context = {
        "articles": page_obj.object_list,
        "has_next": page_obj.has_next(),
        "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        "current_category": category_slug,
    }
    return render(request, "blog/partials/load_response.html", context)


def article_detail(request, slug):
    article = get_object_or_404(
        Article, slug=slug, status="published", published_at__lte=timezone.now()
    )
    return render(request, "blog/detail.html", {"article": article})


@staff_member_required
@require_POST
def tinymce_image_upload(request):
    file = request.FILES.get("file")
    if not file:
        return HttpResponseBadRequest("no file")

    path = default_storage.save(f"blog/content/{file.name}", file)
    url = default_storage.url(path)
    return JsonResponse({"location": url})
