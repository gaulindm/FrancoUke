from django.urls import path

from . import views

app_name = "ratings"

urlpatterns = [
    path("<slug:group_slug>/rate/<int:song_id>/", views.rate_song, name="rate_song"),
    path("<slug:group_slug>/comments/<int:song_id>/", views.song_comments, name="song_comments"),
]
