from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path("", views.home, name="home"),
    path("hero-lab/", views.hero_lab, name="hero_lab"),
]
