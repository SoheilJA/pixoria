from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.urls import path, include, re_path
from django.views.static import serve
from django.contrib.auth import views as auth_views
from apps.core import views as core_views
from django.contrib.sitemaps.views import sitemap
from apps.core.sitemaps import (
    StaticViewSitemap,
    PortfolioSitemap,
    ServiceSitemap,
    ArticleSitemap,
)

handler404 = "config.views.custom_404"

sitemaps = {
    "static": StaticViewSitemap,
    "portfolio": PortfolioSitemap,
    "services": ServiceSitemap,
    "blog": ArticleSitemap,
}


urlpatterns = [
    # مسیرِ ورود به ادمین عمداً مبهم است (who-are-you) تا اسکنرها
    # مسیرِ پیش‌فرضِ /admin/ را پیدا نکنند. نام URL تغییر نکرده است.
    path("who-are-you/", admin.site.urls),
    path("", include("apps.home.urls")),
    path("portfolio/", include("apps.portfolio.urls")),
    path("services/", include("apps.services.urls")),
    path("about/", include("apps.core.urls")),
    path("contact/", include("apps.contact.urls")),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("manifest.webmanifest", core_views.manifest, name="manifest"),
    path("tinymce/", include("tinymce.urls")),
    path("blog/", include("apps.blog.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    re_path(
        r"^public/media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
