# songbook/views/artist_views.py

import math
from collections import Counter, defaultdict

from django.db.models import Q
from django.utils import timezone
from django.views.generic import ListView

from songbook.models import Song
from songbook.mixins import SiteContextMixin
from songbook.views.song_display_views import SongListView


def _sort_name(name):
    """Sort/file key: ignore case and a leading 'The '."""
    n = name.strip().lower()
    return n[4:] if n.startswith("the ") else n


class ArtistListView(SiteContextMixin, ListView):
    template_name = "songbook/artist_list.html"
    context_object_name = "artists"

    def _visible_songs(self):
        """Same visibility rules as SongListView.get_queryset."""
        qs = Song.objects.filter(site_name=self.get_site_name())

        user = self.request.user
        if user.is_authenticated:
            qs = qs.filter(Q(is_public=True) | Q(contributor=user))
        else:
            qs = qs.filter(is_public=True)

        # Xmas songs are hidden outside December
        if timezone.now().month != SongListView.SEASONAL_MONTH:
            qs = qs.exclude(tags__name__iexact=SongListView.SEASONAL_TAG)

        return qs

    def _all_artists(self):
        """
        Every artist with a count of song *families* (distinct titles),
        grouped case-insensitively, so the number matches the rows on the
        'Songs by <artist>' page.
        """
        titles = defaultdict(set)    # artist key -> distinct lowercase titles
        spellings = defaultdict(Counter)  # artist key -> spelling -> uses

        rows = self._visible_songs().values_list("metadata__artist", "songTitle")
        for artist, title in rows:
            artist = (artist or "").strip()
            if not artist:
                continue
            key = artist.lower()
            titles[key].add((title or "").strip().lower())
            spellings[key][artist] += 1

        return [
            {"name": spellings[key].most_common(1)[0][0], "count": len(t)}
            for key, t in titles.items()
        ]

    def get_queryset(self):
        artists = self._all_artists()

        letter = self.kwargs.get("letter")
        if letter:
            artists = [
                a for a in artists
                if _sort_name(a["name"]).startswith(letter.lower())
            ]

        if self.request.GET.get("sort") == "count":
            artists.sort(key=lambda a: (-a["count"], _sort_name(a["name"])))
        else:
            artists.sort(key=lambda a: _sort_name(a["name"]))
        return artists

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artists = context["artists"]  # already filtered and sorted

        # Letter bar is built from ALL artists, not the filtered list
        first_letters = sorted({
            _sort_name(a["name"])[0].upper()
            for a in self._all_artists()
            if _sort_name(a["name"])
        })

        per_col = max(1, math.ceil(len(artists) / 4))
        columns = [artists[i * per_col:(i + 1) * per_col] for i in range(4)]

        context.update(
            {
                "first_letters": first_letters,
                "selected_letter": self.kwargs.get("letter"),
                "artist_columns": columns,
                "sort": self.request.GET.get("sort", "name"),
                "artist_total": len(artists),
                "song_total": sum(a["count"] for a in artists),
            }
        )
        return context