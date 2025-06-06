from django.urls import path
from songbook import views
from .views import (
    SongListView,
    SongCreateView,
    SongUpdateView,
    SongDeleteView,
    UserSongListView,
    ScoreView,
    ArtistListView,
    edit_song_formatting
)

from .views import preview_pdf

#from users.views import update_preferences  # Ensure this import is correct!

from django.shortcuts import redirect

def redirect_to_correct_site(request):
    """Redirect root URL to the correct song list based on hostname."""
    if "FrancoUke" in request.get_host():
        return redirect("francouke_songs")
    else:
        return redirect("strumsphere_songs")


urlpatterns = [
    # 🔹 Homepages for each site
    #path('FrancoUke/', home, {'site_name': 'FrancoUke'}, name='francouke_home'),
    #path('StrumSphere/', home, {'site_name': 'StrumSphere'}, name='strumsphere_home'),
    #path('', SongListView.as_view(), name='songbook-home'),

    path('', redirect_to_correct_site, name='redirect-root'),  # 🔹 Redirect root URL
    
    # 🔹 Song List for Each Site
    path('FrancoUke/songs/', SongListView.as_view(), {'site_name': 'FrancoUke'}, name='francouke_songs'),
    path('StrumSphere/songs/', SongListView.as_view(), {'site_name': 'StrumSphere'}, name='strumsphere_songs'),

    # 🔹 User-Specific Songs (Contributed by User)
    path('FrancoUke/user/<str:username>/', UserSongListView.as_view(), {'site_name': 'FrancoUke'}, name='francouke_user_songs'),
    path('StrumSphere/user/<str:username>/', UserSongListView.as_view(), {'site_name': 'StrumSphere'}, name='strumsphere_user_songs'),

    # 🔹 Individual Song View (Score)
    path('FrancoUke/song/<int:pk>/', ScoreView.as_view(), {'site_name': 'FrancoUke'}, name='francouke_score'),
    path('StrumSphere/song/<int:pk>/', ScoreView.as_view(), {'site_name': 'StrumSphere'}, name='strumsphere_score'),

    # 🔹 Song Creation, Update, and Deletion
    #path('song/new/', SongCreateView.as_view(), name='song-create'),
    #path('song/<int:pk>/update/', SongUpdateView.as_view(), name='song-update'),

    path('FrancoUke/song/new/', SongCreateView.as_view(), {'site_name': 'FrancoUke'}, name='francouke_song_create'),
    path('StrumSphere/song/new/', SongCreateView.as_view(), {'site_name': 'StrumSphere'}, name='strumsphere_song_create'),



    path('FrancoUke/song/<int:pk>/update/', SongUpdateView.as_view(), {'site_name': 'FrancoUke'}, name='francouke_song_update'),
    path('StrumSphere/song/<int:pk>/update/', SongUpdateView.as_view(), {'site_name': 'StrumSphere'}, name='strumsphere_song_update'),

    
    path('song/<int:pk>/delete/', SongDeleteView.as_view(), name='song-delete'),

    # 🔹 PDF Generation
    path("preview_pdf/<int:song_id>/", preview_pdf, name="preview_pdf"),
    path('generate-song-pdf/<int:song_id>/', views.generate_single_song_pdf, name='generate_single_song_pdf'),

    path('generate_multi_song_pdf/', views.generate_multi_song_pdf, name='generate_multi_song_pdf'),

    # 🔹 Artists (Filtering should be site-specific)
    path('FrancoUke/artists/', ArtistListView.as_view(), {'site_name': 'FrancoUke'}, name='francouke_artist_list'),
    path('StrumSphere/artists/', ArtistListView.as_view(), {'site_name': 'StrumSphere'}, name='strumsphere_artist_list'),

    path('FrancoUke/artists/letter/<str:letter>/', ArtistListView.as_view(), {'site_name': 'FrancoUke'}, name='francouke_artist_by_letter'),
    path('StrumSphere/artists/letter/<str:letter>/', ArtistListView.as_view(), {'site_name': 'StrumSphere'}, name='strumsphere_artist_by_letter'),

    path('FrancoUke/artists/<str:artist_name>/', SongListView.as_view(), {'site_name': 'FrancoUke'}, name='francouke_artist_songs'),
    path('StrumSphere/artists/<str:artist_name>/', SongListView.as_view(), {'site_name': 'StrumSphere'}, name='strumsphere_artist_songs'),

    # 🔹 Chord Dictionary
    #path('chord-dictionary/', views.chord_dictionary, name='chord-dictionary'),
    path('FrancoUke/chord-dictionary/', views.chord_dictionary, {'site_name': 'FrancoUke'}, name='francouke_chord_dictionary'),
    path('StrumSphere/chord-dictionary/', views.chord_dictionary, {'site_name': 'StrumSphere'}, name='strumsphere_chord_dictionary'),

    # 🔹 Formatting Editor
    #path("songs/<int:song_id>/edit_formatting/", edit_song_formatting, name="edit_formatting"),

    path('FrancoUke/songs/<int:song_id>/edit_formatting/',  edit_song_formatting, name="francouke_edit_formatting"),
    path('StrumSphere/songs/<int:song_id>/edit_formatting/',  edit_song_formatting, name="strumsphere_edit_formatting"),

    # 🔹 Static Pages
    #path('about/', views.about, name='songbook-about'),
    path('FrancoUke/about/', views.about, {'site_name': 'FrancoUke'}, name='francouke_about'),
    path('StrumSphere/about/', views.about, {'site_name': 'StrumSphere'}, name='strumsphere_about'),


    #path('FrancoUke/whats_new', views.betabugs, name='songbook-betabugs'),
    path('FrancoUke/whats-new/', views.whats_new, {'site_name': 'FrancoUke'}, name='francouke_whats_new'),
    path('StrumSphere/whats-new/', views.whats_new, {'site_name': 'StrumSphere'}, name='strumsphere_whats_new'),
]
