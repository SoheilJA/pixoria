from django.shortcuts import render, get_object_or_404
from .models import Portfolio, Category, PortfolioPageSection


def portfolio_list(request):
    categories = Category.objects.all()
    selected_slug = request.GET.get("category", None)

    if selected_slug:
        selected_category = get_object_or_404(Category, slug=selected_slug)
        portfolios = Portfolio.objects.filter(categories=selected_category)
    else:
        selected_category = None
        portfolios = Portfolio.objects.all()

    context = {
        "portfolios": portfolios,
        "categories": categories,
        "selected_category": selected_category,
        "page_section": PortfolioPageSection.objects.first(),
    }
    return render(request, "portfolio/list.html", context)


def portfolio_detail(request, slug):
    portfolio = get_object_or_404(Portfolio, slug=slug)
    stats = portfolio.stats.all()

    prev_portfolio = (
        Portfolio.objects.filter(order__lt=portfolio.order).order_by("-order").first()
    )
    next_portfolio = (
        Portfolio.objects.filter(order__gt=portfolio.order).order_by("order").first()
    )

    context = {
        "portfolio": portfolio,
        "stats": stats,
        "prev_portfolio": prev_portfolio,
        "next_portfolio": next_portfolio,
    }
    return render(request, "portfolio/detail.html", context)
