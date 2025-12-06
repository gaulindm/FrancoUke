# songbook/views/song_display_views.py

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Q

from songbook.mixins import SiteContextMixin
from songbook.context_processors import site_context
from songbook.models import Song, SongFormatting
from songbook.utils.transposer import extract_chords
from taggit.models import Tag
from users.models import UserPreference

from django.contrib.auth.models import User
from types import SimpleNamespace


# -------------------------------------------------------------
# Landing Page (site-dependent)
# -------------------------------------------------------------
class LandingView(TemplateView):
    """
    Choose a different landing template based on site_name from site_context.
    """
    def get_template_names(self):
        context_data = site_context(self.request)
        site_name = context_data.get("site_name")

        if site_name == "StrumSphere":
            return ["sites/home_strumsphere.html"]
        if site_name == "Uke4ia":
            return ["sites/home_uke4ia.html"]
        return ["sites/home_francouke.html"]


# -------------------------------------------------------------
# List of Songs by a User
# -------------------------------------------------------------
class UserSongListView(ListView):
    model = Song
    template_name = "songbook/user_songs.html"
    context_object_name = "songs"
    ordering = ["songTitle"]
    paginate_by = 15

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        site_name = self.kwargs.get("site_name")
        return Song.objects.filter(contributor=user, site_name=site_name).order_by("songTitle")


# -------------------------------------------------------------
# Score View (detailed view of a single song)
# -------------------------------------------------------------
class ScoreView(DetailView):
    model = Song
    template_name = "songbook/song_simplescore.html"
    context_object_name = "score"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["song"] = self.get_object()

        if self.request.user.is_authenticated:
            preferences, _ = UserPreference.objects.get_or_create(user=self.request.user)
        else:
            preferences = SimpleNamespace(
                font_size=18,
                theme="light",
                auto_scroll=False,
                scroll_speed=20,
            )

        context["preferences"] = preferences
        return context


# -------------------------------------------------------------
# Main Song List View (search, tag filter, artist filter)
# -------------------------------------------------------------
class SongListView(SiteContextMixin, ListView):
    model = Song
    template_name = "songbook/song_list.html"
    context_object_name = "songs"
    ordering = ["songTitle"]
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        site_name = self.get_site_name()
        qs = qs.filter(site_name=site_name)

        if self.request.GET.get("formatted") == "1":
            qs = qs.filter(songformatting__isnull=False)

        search_query = self.request.GET.get("q", "").strip()
        selected_tag = self.request.GET.get("tag", "").strip()
        artist_name = self.kwargs.get("artist_name")

        if search_query:
            qs = qs.filter(
                Q(songTitle__icontains=search_query)
                | Q(metadata__artist__icontains=search_query)
                | Q(metadata__songwriter__icontains=search_query)
            )

        if selected_tag:
            qs = qs.filter(tags__name=selected_tag)

        if artist_name:
            qs = qs.filter(metadata__artist__iexact=artist_name)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        site_name = self.get_site_name()
        context["selected_artist"] = self.kwargs.get("artist_name")
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_tag"] = self.request.GET.get("tag", "")

        # Tags available for that site
        site_songs = Song.objects.filter(site_name=site_name)
        all_tags = Tag.objects.filter(song__in=site_songs).distinct().values_list("name", flat=True)
        context["all_tags"] = all_tags

        # Precomputed data for list rendering
        song_data = []
        for song in context["songs"]:
            parsed_data = song.lyrics_with_chords or ""
            chords = extract_chords(parsed_data, unique=True) if parsed_data else []
            tags = [tag.name for tag in song.tags.all()]
            is_formatted = SongFormatting.objects.filter(song=song).exists()

            song_data.append(
                {
                    "song": song,
                    "chords": ", ".join(chords),
                    "tags": ", ".join(tags),
                    "is_formatted": is_formatted,
                }
            )

        context["song_data"] = song_data
        return context
