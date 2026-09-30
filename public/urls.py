# public/urls.py
from django.urls import path

from . import views

app_name = "public"

urlpatterns = [
    path("", views.public_board, name="public_board"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]