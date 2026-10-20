from django.urls import path

from . import views

app_name = "ratings"

urlpatterns = [
    path("rate/<int:song_id>/", views.rate_song, name="rate_song"),
    path("comments/<int:song_id>/", views.song_comments, name="song_comments"),
    path("notes/", views.NotesInboxView.as_view(), name="notes_inbox"),
    path("notes/<int:rating_id>/delete/", views.delete_note, name="delete_note"),
]