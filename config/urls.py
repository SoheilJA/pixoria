from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.home.urls")),
    path("portfolio/", include("apps.portfolio.urls")),
    path("services/", include("apps.services.urls")),
    path("about/", include("apps.core.urls")),
    path("contact/", include("apps.contact.urls")),
    path("proposal/<slug:slug>/", core_views.proposal, name="proposal"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)