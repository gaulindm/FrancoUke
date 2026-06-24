# songbook/views/song_display_views.py

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Q
from django.contrib.auth import get_user_model
from types import SimpleNamespace
import re

from songbook.mixins import SiteContextMixin
from songbook.context_processors import site_context
from songbook.models import Song, SongFormatting
from songbook.utils.transposer import extract_chords
from taggit.models import Tag
from users.models import UserPreference

User = get_user_model()


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
def is_valid_chord(chord):
        """Only accept strings that look like real chord names."""
        chord = chord.strip()
        pattern = r'^[A-G][#b]?(m|M|maj|min|dim|aug|sus|add|o)?\d*(\(.*?\))?(/[A-G][#b]?)?$'
        return bool(re.match(pattern, chord))


class UserSongListView(SiteContextMixin, ListView):
    """
    Display all songs contributed by a specific user, filtered by site.
    Shows all songs (private + public) if viewing own collection.
    Shows only public songs if viewing someone else's collection.
    """
    model = Song
    template_name = "songbook/user_songs.html"
    context_object_name = "songs"
    paginate_by = 15

    def get_queryset(self):
        self.viewed_user = get_object_or_404(User, username=self.kwargs.get("username"))
        site_name = self.get_site_name()
        
        # 🆕 Privacy filtering
        if self.request.user == self.viewed_user:
            # Viewing your own songs: show ALL (private + public)
            qs = Song.objects.filter(
                contributor=self.viewed_user, 
                site_name=site_name
            )
        else:
            # Viewing someone else's songs: only public ones
            qs = Song.objects.filter(
                contributor=self.viewed_user, 
                site_name=site_name,
                is_public=True
            )
        
        # 🆕 Optional filter by privacy (for "My Collection" filtering)
        privacy_filter = self.request.GET.get('filter')
        if privacy_filter == 'public':
            qs = qs.filter(is_public=True)
        elif privacy_filter == 'private':
            qs = qs.filter(is_public=False)
        
        return qs.order_by("-date_posted")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['viewed_user'] = self.viewed_user
        context['is_own_collection'] = (self.request.user == self.viewed_user)
        
        # 🆕 Add counts for filter tabs (if viewing own collection)
        if context['is_own_collection']:
            all_songs = Song.objects.filter(
                contributor=self.viewed_user,
                site_name=self.get_site_name()
            )
            context['public_count'] = all_songs.filter(is_public=True).count()
            context['private_count'] = all_songs.filter(is_public=False).count()
            context['total_count'] = all_songs.count()
            context['current_filter'] = self.request.GET.get('filter', 'all')
        
        return context


# -------------------------------------------------------------
# ChordSheet View (detailed view of a single song)
# -------------------------------------------------------------
class ChordSheetView(DetailView):
    """
    Display a single song.
    Public songs: anyone can view
    Private songs: only the owner can view
    """
    model = Song
    template_name = "songbook/song_chord_sheet.html"
    context_object_name = "chord_sheet"

    def get_queryset(self):
        # 🆕 Privacy filtering for score view
        qs = super().get_queryset()
        
        if self.request.user.is_authenticated:
            # Show: public songs + user's own songs (public or private)
            qs = qs.filter(
                Q(is_public=True) | Q(contributor=self.request.user)
            )
        else:
            # Anonymous users: only public songs
            qs = qs.filter(is_public=True)
        
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context["song"] = self.get_object()
        

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
        
        # 🆕 Add ownership flag for template
        #context["is_owner"] = (self.request.user == context["song"].contributor)
        context["is_owner"] = (self.request.user == self.object.contributor)

        return context


# -------------------------------------------------------------
# Main Song List View (search, tag filter, artist filter)
# -------------------------------------------------------------
class SongListView(SiteContextMixin, ListView):
    """
    Display all songs for a site.
    Filters by privacy: shows public songs + authenticated user's own songs.
    """
    model = Song
    template_name = "songbook/song_list.html"
    context_object_name = "songs"
    ordering = ["songTitle"]
    paginate_by = 25

    def get_queryset(self):
        chord_filter = self.request.GET.get("chords", "").strip()
        print(f"DEBUG chord_filter: '{chord_filter}'")

        qs = super().get_queryset()
        site_name = self.get_site_name()
        qs = qs.filter(site_name=site_name)

        # Privacy filter
        if self.request.user.is_authenticated:
            qs = qs.filter(
                Q(is_public=True) | Q(contributor=self.request.user)
            )
        else:
            qs = qs.filter(is_public=True)

        # Existing filters
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

        chord_filter = self.request.GET.get("chords", "").strip()
        chord_mode = self.request.GET.get("chord_mode", "playable")  # 🆕 move this outside

        if chord_filter:
            requested_chords = {c.strip().lower() for c in chord_filter.split(",") if c.strip()}

            if chord_mode == "playable":
                matching_pks = []
                for pk, chords_used in qs.values_list("pk", "chords_used"):
                    if chords_used:
                        song_chords = {c.strip().lower() for c in chords_used.split(",")}
                        if song_chords.issubset(requested_chords):
                            matching_pks.append(pk)
                qs = qs.filter(pk__in=matching_pks)

            else:  # contains
                matching_pks = []
                for pk, chords_used in qs.values_list("pk", "chords_used"):
                    if chords_used:
                        song_chords = {c.strip().lower() for c in chords_used.split(",")}
                        if requested_chords.issubset(song_chords):
                            matching_pks.append(pk)
                qs = qs.filter(pk__in=matching_pks)



        return qs.distinct()
    
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        site_name = self.get_site_name()
        context["selected_artist"] = self.kwargs.get("artist_name")
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_tag"] = self.request.GET.get("tag", "")
        context["show_formatted"] = self.request.GET.get("formatted") == "1"
        # 🆕
        context["chord_filter"] = self.request.GET.get("chords", "")

        # Tags
        if self.request.user.is_authenticated:
            site_songs = Song.objects.filter(site_name=site_name).filter(
                Q(is_public=True) | Q(contributor=self.request.user)
            )
        else:
            site_songs = Song.objects.filter(site_name=site_name, is_public=True)

        all_tags = Tag.objects.filter(song__in=site_songs).distinct().values_list("name", flat=True)
        context["all_tags"] = all_tags

        # 🆕 All unique chords across the site for the clickable buttons
        # In get_context_data():
        all_chords = set()
        for song in site_songs:
            if song.chords_used:
                for chord in song.chords_used.split(","):
                    chord = chord.strip()
                    if is_valid_chord(chord):
                        all_chords.add(chord)
        context["all_chords"] = sorted(all_chords)
        context["chord_filter"] = self.request.GET.get("chords", "")
        context["chord_mode"] = self.request.GET.get("chord_mode", "playable")

        # Song data
        song_data = []
        for song in context["songs"]:
            parsed_data = song.lyrics_with_chords or ""
            chords = extract_chords(parsed_data, unique=True) if parsed_data else []
            tags = [tag.name for tag in song.tags.all()]
            is_formatted = SongFormatting.objects.filter(song=song).exists()
            song_data.append({
                "song": song,
                "chords": ", ".join(chords),
                "tags": ", ".join(tags),
                "is_formatted": is_formatted,
            })

        context["song_data"] = song_data
        return context