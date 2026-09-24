# public/urls.py
from django.urls import path

from . import views

app_name = "public"

urlpatterns = [
    path("", views.public_board, name="public_board"),
]