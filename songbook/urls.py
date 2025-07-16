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
    # 🔹 Home / Song List View
    path('', SongListView.as_view(), name='song-list'),
###Latest one
    path('', SongListView.as_view(), name='home'),  # 👈 This is critical!
    path('artists/', ArtistListView.as_view(), name='artist_list'),
    path('chord-dictionary/', chord_dictionary, name='chord-dictionary'),
    path('about/', views.about, name='songbook-about'),
    #path('whats-new/', views.whats_new, name='whats_new'),
    path('song/new/', SongCreateView.as_view(), name='song-create'),




    # 🔹 Artists
    path('artists/', ArtistListView.as_view(), name='artist_list'),
    path('artists/letter/<str:letter>/', ArtistListView.as_view(), name='artist_by_letter'),
    path('artists/<str:artist_name>/', SongListView.as_view(), name='artist_songs'),

    # 🔹 Song Create / Update / Delete
    path('song/new/', SongCreateView.as_view(), name='song-create'),
    path('song/<int:pk>/', ScoreView.as_view(), name='score-view'),
    path('song/<int:pk>/update/', SongUpdateView.as_view(), name='song_update'),
    path('song/<int:pk>/delete/', SongDeleteView.as_view(), name='song_delete'),

    # 🔹 Songs contributed by specific user
    path('user/<str:username>/', UserSongListView.as_view(), name='user-songs'),

    # 🔹 Song Formatting
    path('songs/<int:song_id>/edit_formatting/', edit_song_formatting, name='edit_formatting'),

    # 🔹 Chord Dictionary
    path('chord-dictionary/', chord_dictionary, name='chord_dictionary'),

    # 🔹 PDF Generation
    path('preview_pdf/<int:song_id>/', preview_pdf, name='preview_pdf'),
    path('generate-song-pdf/<int:song_id>/', views.generate_single_song_pdf, name='generate_single_song_pdf'),
    path('generate_multi_song_pdf/', views.generate_multi_song_pdf, name='generate_multi_song_pdf'),



    # 🔹 Static / Informational Views
    #path('about/', views.about, name='songbook-about'),
    path('whats-new/', whats_new, name='whats_new'),
]
