from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.home.urls")),
    path("portfolio/", include("app.portfolio.urls")),
    path("services/", include("apps.services.urls")),
    path("about/", include("apps.contact.urls")),
    path("contact/", include("apps.contact.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
