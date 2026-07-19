from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from config.views import custom_404

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.home.urls")),
    path("portfolio/", include("apps.portfolio.urls")),
    path("services/", include("apps.services.urls")),
    path("about/", include("apps.core.urls")),
    path("contact/", include("apps.contact.urls")),
    path("test-404/", lambda request: custom_404(request, None)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "config.views.custom_404"
# handler500 = 'config.views.custom_500'  # اگر خواستی 500 هم اضافه کنی
