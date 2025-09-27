from django.urls import path
from .views import (
    SongListView,
    SongCreateView,
    SongUpdateView,
    SongDeleteView,
    UserSongListView,
    ScoreView,
    ArtistListView,
    edit_song_formatting,
    chord_dictionary,
    generate_single_song_pdf,
    generate_multi_song_pdf,
    preview_pdf,
    about,
    whats_new,
)
from songbook import views

app_name = "songbook"

urlpatterns = [
    # 🔹 Home
    path("", views.LandingView.as_view(), name="home"),  # ✅ Landing page


    # 🔹 Songs
    path("songs/", views.SongListView.as_view(), name="song_list"),
    path("songs/new/", views.SongCreateView.as_view(), name="song_create"),
    path("songs/<int:pk>/", views.ScoreView.as_view(), name="score_view"),
    path("songs/<int:pk>/edit/", views.SongUpdateView.as_view(), name="song_update"),
    path("songs/<int:pk>/delete/", views.SongDeleteView.as_view(), name="song_delete"),

    # 🔹 Artists
    path("artists/", views.ArtistListView.as_view(), name="artist_list"),
    path("artists/<str:artist_name>/", views.SongListView.as_view(), name="songs_by_artist"),
    path("artists/letter/<str:letter>/", views.ArtistListView.as_view(), name="artist_by_letter"),

    # 🔹 Chords 
    path("chords/", views.chord_dictionary, name="chord_dictionary"),

    # 🔹 Tags (Optional)
    path("tags/<str:tag_name>/", views.SongListView.as_view(), name="songs_by_tag"),

    # 🔹 Legacy FBVs (to be refactored)
    path("about/", views.about, name="about"),
    path("whats-new/", views.whats_new, name="whats_new"),

     # 🔹 Song Formatting
    path('songs/<int:song_id>/edit_formatting/', edit_song_formatting, name='edit_formatting'),




    # 🔹 PDF Generation
    path('preview_pdf/<int:song_id>/', preview_pdf, name='preview_pdf'),

    path('generate-song-pdf/<int:song_id>/', views.generate_single_song_pdf, name='generate_single_song_pdf'),
    path('generate_multi_song_pdf/', views.generate_multi_song_pdf, name='generate_multi_song_pdf'),


    # 🔹 Static / Informational Views
    #path('about/', views.about, name='songbook-about'),
    path('whats-new/', whats_new, name='whats_new'),
]
