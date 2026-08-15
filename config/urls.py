from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from apps.core import views as core_views
from django.contrib.sitemaps.views import sitemap
from apps.core.sitemaps import StaticViewSitemap, PortfolioSitemap, ServiceSitemap

handler404 = "config.views.custom_404"

sitemaps = {
    "static": StaticViewSitemap,
    "portfolio": PortfolioSitemap,
    "services": ServiceSitemap,
}


urlpatterns = [
    path("admin/", admin.site.urls),
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
    path("proposal/<slug:slug>/", core_views.proposal, name="proposal"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
