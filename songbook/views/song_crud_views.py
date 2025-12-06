# songbook/views/song_crud_views.py

from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from songbook.models import Song
from songbook.context_processors import site_context
from songbook.parsers import parse_song_data


class SongCreateView(LoginRequiredMixin, CreateView):
    model = Song
    fields = [
        "songTitle",
        "songChordPro",
        "metadata",
        "revised_on",
        "tags",
        "acknowledgement",
    ]

    def form_valid(self, form):
        form.instance.contributor = self.request.user
        context_data = site_context(self.request)
        form.instance.site_name = context_data.get("site_name")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site_context(self.request))
        return context

    def get_success_url(self):
        site_name = self.object.site_name or site_context(self.request)["site_name"]
        return reverse(f"{site_name.lower()}:score_view", kwargs={"pk": self.object.pk})


class SongUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Song
    fields = [
        "songTitle",
        "songChordPro",
        "lyrics_with_chords",
        "metadata",
        "revised_on",
        "tags",
        "acknowledgement",
    ]

    def test_func(self):
        # Allow only logged-in users (actual ownership enforced in delete view)
        return self.request.user.is_authenticated

    def form_valid(self, form):
        # Convert raw ChordPro into parsed lyrics_with_chords
        raw_lyrics = form.cleaned_data.get("songChordPro", "")
        try:
            parsed_lyrics = parse_song_data(raw_lyrics)
        except Exception as e:
            form.add_error("songChordPro", f"Error parsing song data: {e}")
            return self.form_invalid(form)

        form.instance.lyrics_with_chords = parsed_lyrics
        form.instance.contributor = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site_context(self.request))
        return context

    def get_success_url(self):
        site_name = self.object.site_name or site_context(self.request)["site_name"]
        return reverse(f"{site_name.lower()}:score_view", kwargs={"pk": self.object.pk})


class SongDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Song
    success_url = reverse_lazy("songbook-home")

    def test_func(self):
        song = self.get_object()
        return self.request.user == song.contributor
