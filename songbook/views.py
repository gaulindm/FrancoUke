"""
songbook/views.py — cleaned and consolidated.

Features:
- edit_song_formatting (permissions-protected)
- ArtistListView
- LandingView (per-site template selection)
- UserSongListView
- ScoreView (detail view for a song)
- SongListView (site-scoped listing with search/tag/artist filters)
- SongCreateView, SongUpdateView, SongDeleteView
- PDF helpers + endpoints (single, multiple, preview)
- Chord JSON endpoints + chord lookup
- chord_dictionary, about, whats_new
- save_scroll_speed (simple AJAX endpoint)
"""

import json
import logging
import os
from collections import defaultdict
from django.db.models import Q

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
)

from taggit.models import Tag

from .context_processors import site_context
from .forms import SongFormattingForm
from .mixins import SiteContextMixin
from .models import Song, SongFormatting
from .parsers import parse_song_data
from songbook.utils.pdf_generator import generate_songs_pdf, load_chords
from songbook.utils.transposer import extract_chords, transpose_lyrics
from users.models import UserPreference

import re
from django.shortcuts import render
from songbook.utils.chord_utils import load_chords, render_chord_svg
import io
from django.http import HttpResponse
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics import renderPM





logger = logging.getLogger(__name__)



# Allowed instruments for chord JSON endpoints
ALLOWED_INSTRUMENTS = {
    "ukulele",
    "guitar",
    "guitalele",
    "banjo",
    "mandolin",
    "baritoneUke",
}


# ---------------------------------------------------------------------
# Formatting editor (per-user song formatting)
# ---------------------------------------------------------------------
@login_required
@permission_required("songbook.change_songformatting", raise_exception=True)
def edit_song_formatting(request, song_id):
    """
    Edit per-user SongFormatting with a dual-edit copy-from-Gaulind on first creation.
    """
    context_data = site_context(request)
    # Ensure formatting exists for (user, song)
    formatting, created = SongFormatting.objects.get_or_create(
        user=request.user,
        song_id=song_id,
        defaults={
            "intro": {},
            "verse": {},
            "chorus": {},
            "bridge": {},
            "interlude": {},
            "outro": {},
            "centered": {},  # ✅ add this

        },
    )

    # If just created, attempt to copy Gaulind's formatting (if present)
    if created:
        gaulind_formatting = SongFormatting.objects.filter(user__username="Gaulind", song_id=song_id).first()
        if gaulind_formatting:
            for section in ["intro", "verse", "chorus", "bridge", "interlude", "outro"]:
                setattr(formatting, section, getattr(gaulind_formatting, section))
            formatting.save()

    if request.method == "POST":
        form = SongFormattingForm(request.POST, instance=formatting)
        if form.is_valid():
            form.save()
            messages.success(request, "Formatting updated successfully!")
            return redirect(f"{context_data['site_namespace']}:score_view", pk=song_id)
    else:
        form = SongFormattingForm(instance=formatting)

    return render(
        request,
        "songbook/edit_formatting.html",
        {
            "form": form,
            "pk": song_id,
            "formatting": formatting,
            **context_data,
        },
    )


# ---------------------------------------------------------------------
# Artist listing
# ---------------------------------------------------------------------
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
        artists = [a for a in artists_qs if a]  # Remove empty/None
        letter = self.kwargs.get("letter")

        if letter:
            artists = [a for a in artists if a.upper().startswith(letter.upper())]

        return sorted(artists)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_artists = self.get_queryset()
        first_letters = sorted({a[0].upper() for a in all_artists if a})
        context.update(
            {
                "first_letters": first_letters,
                "selected_letter": self.kwargs.get("letter"),
                "artist_columns": [all_artists[i::4] for i in range(4)],
            }
        )
        return context


# ---------------------------------------------------------------------
# PDF helpers and endpoints
# ---------------------------------------------------------------------
from django.contrib.auth.models import AnonymousUser

def generate_pdf_response(filename, songs, user=None, transpose_value=0, formatting=None, site_name=None, inline=False):
    content_type = "application/pdf"
    response = HttpResponse(content_type=content_type)
    disposition_type = "inline" if inline else "attachment"
    response["Content-Disposition"] = f'{disposition_type}; filename="{filename}.pdf"'

    generate_songs_pdf(response, songs, user, transpose_value, formatting, site_name=site_name)
    return response



def generate_multi_song_pdf(request):
    """
    POST endpoint to generate a PDF of songs filtered by tag (expects 'tag_name' in POST).
    """
    tag_name = request.POST.get("tag_name", "").strip()
    if not tag_name:
        return JsonResponse({"error": "Missing tag_name"}, status=400)

    songs = Song.objects.filter(tags__name=tag_name)
    return generate_pdf_response("multi_song_report", songs, user=request.user)


@login_required
def generate_single_song_pdf(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    context_data = site_context(request)
    site_name = context_data.get("site_name")
    return generate_pdf_response(
        filename=song.songTitle,
        songs=[song],
        user=request.user,
        transpose_value=0,
        formatting=None,
        site_name=site_name,
        inline=True,
    )


def preview_pdf(request, song_id):
    """
    Preview a single-song PDF (inline). Accepts optional ?transpose=<int>.
    """
    song = get_object_or_404(Song, pk=song_id)
    transpose_value = int(request.GET.get("transpose", "0") or 0)

    # Do not modify DB object in-place: create a shallow copy for preview
    preview_song = song
    if transpose_value != 0 and preview_song.lyrics_with_chords:
        # produce a transposed preview string and attach temporarily to the object
        preview_song = Song(
            **{f.name: getattr(song, f.name) for f in song._meta.fields}
        )
        preview_song.lyrics_with_chords = transpose_lyrics(song.lyrics_with_chords, transpose_value)

    site_name = site_context(request).get("site_name")
    return generate_pdf_response(
        filename=f"{song.songTitle}_preview",
        songs=[preview_song],
        user=request.user if request.user.is_authenticated else None,
        transpose_value=transpose_value,
        formatting=None,
        site_name=site_name,
        inline=True,
    )


# ---------------------------------------------------------------------
# Chord JSON endpoints and dictionary page
# ---------------------------------------------------------------------
def serve_chords_json(request, instrument):
    """
    Serve chord definitions from songbook/chords/<instrument>.json
    """
    if instrument not in ALLOWED_INSTRUMENTS:
        raise Http404("Instrument not supported")

    file_path = os.path.join(settings.BASE_DIR, "songbook", "chords", f"{instrument}.json")
    if not os.path.exists(file_path):
        raise Http404("Chord file not found")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return JsonResponse(json.load(f), safe=False)
    except Exception as e:
        logger.exception("Failed to load chord JSON for %s: %s", instrument, e)
        raise Http404(f"Invalid JSON: {e}")


def get_chord_definition(request, chord_name):
    """
    Return a JSON object describing a chord by name (case-insensitive).
    Relies on load_chords() util.
    """
    chords = load_chords()
    for chord in chords:
        if chord.get("name", "").lower() == chord_name.lower():
            return JsonResponse({"success": True, "chord": chord})
    return JsonResponse({"success": False, "error": f"Chord '{chord_name}' not found."})


#def chord_dictionary(request):
    """
    Render a human-facing chord dictionary page (uses site_context).
    """
 #   context_data = site_context(request)
 #   return render(request, "chords/chord_dictionary.html", context_data)


# ---------------------------------------------------------------------
# Simple AJAX endpoint: save scroll speed for a song
# ---------------------------------------------------------------------
@csrf_exempt  # Keep for legacy clients; remove if you enforce CSRF via fetch/XHR tokens
def save_scroll_speed(request, song_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        new_speed = int(payload.get("scroll_speed", 20))
    except Exception:
        return JsonResponse({"error": "Invalid payload"}, status=400)

    try:
        song = Song.objects.get(pk=song_id)
        song.scroll_speed = new_speed
        song.save(update_fields=["scroll_speed"])
        return JsonResponse({"status": "ok", "scroll_speed": new_speed})
    except Song.DoesNotExist:
        return JsonResponse({"error": "Song not found"}, status=404)


# ---------------------------------------------------------------------
# Site landing + lists + CRUD views
# ---------------------------------------------------------------------
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

from types import SimpleNamespace

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
            # Anonymous default preferences
            preferences = SimpleNamespace(
                font_size=18,
                theme="light",
                auto_scroll=False,
                scroll_speed=20,
            )

        context["preferences"] = preferences
        return context


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

        # formatted filter
        if self.request.GET.get("formatted") == "1":
            qs = qs.filter(songformatting__isnull=False)

        # search and tag filters
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

        # Tags for the site
        site_songs = Song.objects.filter(site_name=site_name)
        all_tags = Tag.objects.filter(song__in=site_songs).distinct().values_list("name", flat=True)
        context["all_tags"] = all_tags

        # Precompute song_data (chords, tags, formatted flag) for list rendering
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


class SongCreateView(LoginRequiredMixin, CreateView):
    model = Song
    fields = ["songTitle", "songChordPro", "metadata", "revised_on", "tags", "acknowledgement"]

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
    fields = ["songTitle", "songChordPro", "lyrics_with_chords", "metadata", "revised_on", "tags", "acknowledgement"]

    def test_func(self):
        # Allow only authenticated users (actual contributor check enforced in test_func of delete view)
        return self.request.user.is_authenticated

    def form_valid(self, form):
        # Parse the raw chordpro input into lyrics_with_chords
        raw_lyrics = form.cleaned_data.get("songChordPro", "")
        try:
            parsed_lyrics = parse_song_data(raw_lyrics)
        except Exception as e:
            form.add_error("songChordPro", f"Error parsing song data: {e}")
            return self.form_invalid(form)

        form.instance.lyrics_with_chords = parsed_lyrics
        form.instance.contributor = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        site_name = self.object.site_name or site_context(self.request)["site_name"]
        return reverse(f"{site_name.lower()}:score_view", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site_context(self.request))
        return context


class SongDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Song
    success_url = reverse_lazy("songbook-home")

    def test_func(self):
        song = self.get_object()
        return self.request.user == song.contributor


# ---------------------------------------------------------------------
# Simple static-ish pages
# ---------------------------------------------------------------------
def about(request):
    return render(request, "songbook/about.html", site_context(request))


def whats_new(request):
    return render(request, "songbook/whats_new.html", site_context(request))

ROOTS = ["C", "C#","D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

CHORD_TABS = {
    "triads":     ["", "m", "aug", "dim"],
    "sevenths":   ["7", "m7", "M7", "aug7", "dim7", "m7b5", "mMaj7"],
    "suspended":  ["sus2", "sus4", "7sus2", "7sus4"],
    "extended":   ["9", "m9", "M9", "11", "m11", "13", "m13"],
    "added":      ["5", "6", "m6", "add9", "madd9"],
}

INSTRUMENTS = [
    "ukulele", "guitalele", "guitar",
    "banjo", "mandolin", "baritone_ukulele"
]


def chord_dictionary(request):
    instrument = request.GET.get("instrument", "ukulele")
    site_name = request.resolver_match.namespace
    lefty = request.GET.get("lefty") in ["1", "true", "on"]
    show_alt = request.GET.get("show_alt") in ["1", "true", "on"]

    # Selected tab (triads default)
    tab = request.GET.get("tab", "triads")
    allowed_types = CHORD_TABS.get(tab, CHORD_TABS["triads"])

    # Load chord JSON
    chords = load_chords(instrument)

    # grouped[root][ctype] = list of variations
    grouped = {r: {} for r in ROOTS}

    for chord in chords:
        name = chord.get("name")
        variations_raw = chord.get("variations", [])
        if not name or not variations_raw:
            continue

        # Extract root + type
        m = re.match(r"([A-G][b#]?)(.*)", name)
        if not m:
            continue

        root = m.group(1)
        ctype = m.group(2) or ""

        # Skip types not in the current tab
        if ctype not in allowed_types:
            continue

        # Build variation objects
        variations = []
        for v in variations_raw:

            main_svg = render_chord_svg(
                name,
                v,
                instrument,
                is_lefty=lefty,
                scale=1.0
            )

            small_svg = render_chord_svg(
                name,
                v,
                instrument,
                is_lefty=lefty,
                scale=0.5
            )

            variations.append({
                "name": name,
                "main_svg": main_svg,
                "small_svg": small_svg,
            })

        grouped[root][ctype] = variations

    # Build rows (one row per type)
    rows = []
    for ctype in allowed_types:
        row = {"type": ctype, "cells": []}

        for root in ROOTS:
            variations = grouped.get(root, {}).get(ctype)

            if not variations:
                row["cells"].append(None)
                continue

            # Main = always first variation
            main = variations[0]

            # Alternate variations (only if show_alt ON)
            smalls = [v["small_svg"] for v in variations[1:3]] if show_alt else []

            row["cells"].append({
                "name": main["name"],
                "main_svg": main["main_svg"],
                "small_svgs": smalls,
            })

        rows.append(row)

    context = {
        "site_name": site_name,
        "instrument": instrument,
        "lefty": lefty,
        "show_alt": show_alt,
        "tab": tab,
        "roots": ROOTS,

        "rows": rows,
        "instruments": INSTRUMENTS,
        "CHORD_TABS": CHORD_TABS,
    }

    return render(request, "chords/chord_dictionary.html", context)
