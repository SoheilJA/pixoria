from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from apps.core.context_utils import crumbs
from .models import Portfolio, Category, PortfolioPageSection


def portfolio_list(request):
    categories = Category.objects.all()
    selected_slug = request.GET.get("category")

    # همهٔ پروژه‌ها به مشتری پاس داده می‌شوند؛ فیلترِ دسته‌بندی در مرورگر
    # انجام می‌شود (مثل بخش نمونه‌کارهای صفحهٔ اصلی) تا جابه‌جایی بین دسته‌ها
    # بدون بارگذاریِ دوبارهٔ صفحه باشد. ?category= فقط دستهٔ فعالِ اولیه را
    # مشخص می‌کند و یک اسلاگِ نامعتبر کل صفحه را ۴۰۴ نمی‌کند.
    portfolios = list(
        Portfolio.objects.prefetch_related("categories").order_by("order", "id")
    )
    selected_category = (
        categories.filter(slug=selected_slug).first() if selected_slug else None
    )

    context = {
        "crumbs": crumbs(("خانه", "home:home"), ("نمونه‌کارها", None)),
        "portfolios": portfolios,
        "categories": categories,
        "selected_category": selected_category,
        "page_section": PortfolioPageSection.objects.first(),
    }
    return render(request, "portfolio/list.html", context)


def portfolio_detail(request, slug):
    portfolio = get_object_or_404(
        Portfolio.objects.select_related("testimonial")
        .prefetch_related("categories", "stats", "gallery"),
        slug=slug,
    )

    # پروژهٔ قبلی و بعدی — ترتیب یکسان با آرشیو (order، سپس id) تا لینک‌ها
    # دقیقاً همسایهٔ پروژهٔ فعلی در لیست باشند؛ مقایسهٔ order به‌تنهایی
    # پروژه‌های هم‌ترتیب را نادیده می‌گرفت.
    prev_portfolio = (
        Portfolio.objects.filter(Q(order__lt=portfolio.order) | Q(order=portfolio.order, id__lt=portfolio.id))
        .order_by("-order", "-id")
        .first()
    )
    next_portfolio = (
        Portfolio.objects.filter(Q(order__gt=portfolio.order) | Q(order=portfolio.order, id__gt=portfolio.id))
        .order_by("order", "id")
        .first()
    )

    context = {
        "crumbs": crumbs(
            ("خانه", "home:home"),
            ("نمونه‌کارها", "portfolio:list"),
            (portfolio.title, None),
        ),
        "portfolio": portfolio,
        "prev_portfolio": prev_portfolio,
        "next_portfolio": next_portfolio,
    }
    return render(request, "portfolio/detail.html", context)
