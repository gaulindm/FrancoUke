from django.urls import path
#from songbook import legacy_views as views
from songbook.views.formatting_views import edit_song_formatting
from songbook.views.misc_views import about, whats_new, save_scroll_speed
from songbook.views.artist_views import ArtistListView

from songbook.views.pdf_views import (
    generate_pdf_response,    # if you expose it
    generate_multi_song_pdf,
    generate_single_song_pdf,
    preview_pdf,
)

from songbook.views.song_crud_views import (SongCreateView, SongUpdateView, SongDeleteView,)
from songbook.views.song_display_views import (LandingView, UserSongListView, ScoreView, SongListView,)
from songbook.views.chord_views import (chord_dictionary, serve_chords_json, get_chord_definition,)

app_name = "songbook"

urlpatterns = [
    # 🔹 Home
    path("", LandingView.as_view(), name="home"),

    # 🔹 Songs
    path("songs/", SongListView.as_view(), name="song_list"),
    path("songs/new/", SongCreateView.as_view(), name="song_create"),
    path("songs/<int:pk>/", ScoreView.as_view(), name="score_view"),
    path("songs/<int:pk>/edit/", SongUpdateView.as_view(), name="song_update"),
    path("songs/<int:pk>/delete/", SongDeleteView.as_view(), name="song_delete"),

    # 🔹 Artists
    path("artists/", ArtistListView.as_view(), name="artist_list"),
    path("artists/<str:artist_name>/", SongListView.as_view(), name="songs_by_artist"),
    path("artists/letter/<str:letter>/", ArtistListView.as_view(), name="artist_by_letter"),

    # 🔹 Chords (refactored)
    path("chords/", chord_dictionary, name="chord_dictionary"),
    path("chords/<str:instrument>.json", serve_chords_json, name="serve_chords_json"),
    path("api/chord/<str:chord_name>/", get_chord_definition, name="get_chord_definition"),

    # 🔹 Tags
    path("tags/<str:tag_name>/", SongListView.as_view(), name="songs_by_tag"),

    # 🔹 Formatting
    path("songs/<int:song_id>/edit_formatting/", edit_song_formatting, name="edit_formatting"),

    # 🔹 PDF Generation
    path("preview_pdf/<int:song_id>/", preview_pdf, name="preview_pdf"),
    path("generate-song-pdf/<int:song_id>/", generate_single_song_pdf, name="generate_single_song_pdf"),
    path("generate_multi_song_pdf/", generate_multi_song_pdf, name="generate_multi_song_pdf"),

    # 🔹 AJAX scroll speed
    path("song/<int:song_id>/save_scroll_speed/", save_scroll_speed, name="save_scroll_speed"),

    path('user/<str:username>/', UserSongListView.as_view(), name='user-songs'),
    


    # 🔹 Static
    path("about/", about, name="about"),
    path("whats-new/", whats_new, name="whats_new"),
]
