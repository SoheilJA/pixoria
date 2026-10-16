from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.portfolio.models import Portfolio
from apps.services.models import Service
from apps.blog.models import Article


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return [
            "home:home",
            "portfolio:list",
            "services:list",
            "core:about",
            "contact:contact",
        ]

    def location(self, item):
        return reverse(item)


class PortfolioSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return Portfolio.objects.all()

    def location(self, obj):
        return reverse("portfolio:detail", args=[obj.slug])


class ServiceSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Service.objects.all()

    def location(self, obj):
        return reverse("services:detail", args=[obj.slug])


class ArticleSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return Article.objects.filter(status="published")

    def location(self, obj):
        return reverse("blog:detail", args=[obj.slug])

    def lastmod(self, obj):
        return obj.updated_at
