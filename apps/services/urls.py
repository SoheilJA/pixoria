from django.urls import path
from . import views

app_name = "services"

urlpatterns = [
    path("", views.services_list, name="list"),
    path("<slug:slug>/", views.services_detail, name="detail"),
]
