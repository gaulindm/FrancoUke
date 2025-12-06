# songbook/views/artist_views.py

from django.views.generic import ListView
from django.db.models import Q

from songbook.models import Song
from songbook.mixins import SiteContextMixin


class ArtistListView(SiteContextMixin, ListView):
    template_name = "songbook/artist_list.html"
    context_object_name = "artists"

    def get_queryset(self):
        site_name = self.get_site_name()
        artists_qs = (
            Song.objects.filter(site_name=site_name)
            .values_list("metadata__artist", flat=True)
            .distinct()
        )

        artists = [a for a in artists_qs if a]  # Remove empty / None
        letter = self.kwargs.get("letter")

        if letter:
            artists = [a for a in artists if a.upper().startswith(letter.upper())]

        return sorted(artists)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_artists = self.get_queryset()

        first_letters = sorted({a[0].upper() for a in all_artists if a})

        # 4 columns for UI layout
        context.update(
            {
                "first_letters": first_letters,
                "selected_letter": self.kwargs.get("letter"),
                "artist_columns": [all_artists[i::4] for i in range(4)],
            }
        )

        return context
