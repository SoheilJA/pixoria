from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.article_list, name="list"),
    path("load/", views.load_articles, name="load"),
    path(
        "tinymce-image-upload/", views.tinymce_image_upload, name="tinymce_image_upload"
    ),
    path("<slug:slug>/", views.article_detail, name="detail"),
]
