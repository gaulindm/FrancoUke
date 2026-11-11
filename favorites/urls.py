# favorites/urls.py
from django.urls import path

from . import views

app_name = "favorites"

urlpatterns = [
    path("toggle/<int:song_id>/", views.toggle_favorite, name="toggle"),
    path("top/", views.top_favorites, name="top"),
]