from django.urls import path
from . import views

app_name = "francontcube"

urlpatterns = [
    path("", views.home, name="home"),
    path("slides/", views.slides, name="slides"),
    path("pdfs/", views.pdfs, name="pdfs"),
    path("videos/", views.videos, name="videos"),
]
