# songbook/views.py
import json
import logging
import os
from pathlib import Path
from collections import defaultdict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.functions import Cast, Lower
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from taggit.models import Tag

from .context_processors import site_context
from .forms import SongForm, SongFormattingForm, TagFilterForm
from .mixins import SiteContextMixin
from .models import Song, SongFormatting
from .parsers import parse_song_data
from songbook.context_processors import site_context as _site_context  # alias to avoid accidental override
from songbook.utils.ABC2audio import convert_abc_to_audio
from songbook.utils.pdf_generator import generate_songs_pdf, load_chords
from songbook.utils.transposer import extract_chords, transpose_lyrics

logger = logging.getLogger(__name__)

# Directory for chord JSON files relative to this file
CHORDS_DIR = Path(__file__).resolve().parent / "chords"


# ---------------------------------------------------------------------------
# Helpers / Mixins
# ---------------------------------------------------------------------------
class ContributorOrAdminMixin(UserPassesTestMixin):
    """
    Allow access if the requesting user is the object's contributor or is staff.
    Expects the view to implement `get_object()`.
    """

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        try:
            obj = self.get_object()
        except Exception:
            return False
        # Allow if the user is the contributor or has staff privileges
        return getattr(obj, "contributor", None) == user or user.is_staff

    def handle_no_permission(self):
        # For consistency, raise PermissionDenied for non-authorized attempts
        raise PermissionDenied


# ---------------------------------------------------------------------------
# Function-based views
# ---------------------------------------------------------------------------
@login_required
@permission_required("songbook.change_songformatting", raise_exception=True)
def edit_song_formatting(request, song_id):
    """Edit or create per-user SongFormatting (Dual Edition support)."""
    context_data = site_context(request)
    site_name = context_data.get("site_name")

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
        },
    )

    # If newly created, try to copy formatting from a default user (Gaulind) if available
    if created:
        gaulind_formatting = SongFormatting.objects.filter(
            user__username="Gaulind", song_id=song_id
        ).first()
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


def preview_pdf(request, song_id):
    """
    Public preview of a song as a PDF (inline).
    `transpose` may be passed as GET param.
    """
    song = get_object_or_404(Song, pk=song_id)

    transpose_value = int(request.GET.get("transpose", 0) or 0)
    # create a shallow copy to avoid persisting changes on Song model
    preview_song = song
    if transpose_value != 0 and getattr(preview_song, "lyrics_with_chords", None):
        preview_song.lyrics_with_chords = transpose_lyrics(preview_song.lyrics_with_chords, transpose_value)

    context_data = site_context(request)
    site_name = context_data.get("site_name")

    response = HttpResponse(content_type="application/pdf")
    safe_title = f"{song.songTitle or 'song'}_preview.pdf"
    response["Content-Disposition"] = f'inline; filename="{safe_title}"'
    generate_songs_pdf(response, [preview_song], request.user if request.user.is_authenticated else None, transpose_value, None, site_name=site_name)
    return response


def generate_pdf_response(filename, songs, user=None):
    """Reusable function to generate and return a PDF response for download."""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
    generate_songs_pdf(response, songs, user)
    return response


@login_required
def generate_multi_song_pdf(request):
    """
    Generates a PDF for multiple songs filtered by tag.
    Requires POST with 'tag_name'.
    """
    tag_name = request.POST.get("tag_name", "").strip()
    if not tag_name:
        return JsonResponse({"success": False, "error": "No tag_name provided"}, status=400)

    songs = Song.objects.filter(tags__name=tag_name)
    return generate_pdf_response("multi_song_report", songs, request.user)


@login_required
def generate_single_song_pdf(request, song_id):
    """
    Return an inline PDF for a single song. Auth required.
    """
    song = get_object_or_404(Song, pk=song_id)
    context_data = site_context(request)
    site_name = context_data.get("site_name")

    response = HttpResponse(content_type="application/pdf")
    safe_filename = f"{song.songTitle or 'song'}.pdf"
    response["Content-Disposition"] = f'inline; filename="{safe_filename}"'
    generate_songs_pdf(response, [song], request.user, transpose_value=0, formatting=None, site_name=site_name)
    return response


def serve_chords_json(request, instrument):
    """
    Serve chord definitions (JSON) from songbook/chords/<instrument>.json
    Public endpoint.
    """
    allowed_instruments = {
        "ukulele",
        "guitar",
        "guitalele",
        "banjo",
        "mandolin",
        "baritoneUke",
    }

    if instrument not in allowed_instruments:
        raise Http404("Instrument not supported")

    file_path = CHORDS_DIR / f"{instrument}.json"
    if not file_path.exists():
        raise Http404("Chord file not found")

    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise Http404(f"Invalid JSON: {e}")

    return JsonResponse(data, safe=False)


def get_chord_definition(request, chord_name):
    """
    Fetch the definition of a single chord by name (searches through loaded chords).
    """
    chords = load_chords()
    for chord in chords:
        if chord.get("name", "").lower() == chord_name.lower():
            return JsonResponse({"success": True, "chord": chord})
    return JsonResponse({"success": False, "error": f"Chord '{chord_name}' not found."}, status=404)


def chord_dictionary(request):
    """Render a page showing the chord dictionary."""
    context_data = site_context(request)
    return render(request, "songbook/chord_dictionary.html", context_data)


def home(request, site_name):
    return render(request, "index.html", {"site_name": site_name})


def about(request):
    return render(request, "songbook/about.html", site_context(request))


def whats_new(request):
    return render(request, "songbook/whats_new.html", site_context(request))


# ---------------------------------------------------------------------------
# Class-based views
# ---------------------------------------------------------------------------
class LandingView(TemplateView):
    """
    Returns a site-specific landing template based on site_name in context.
    """
    def get_template_names(self):
        context_data = site_context(self.request)
        site_name = context_data.get("site_name")
        if site_name == "StrumSphere":
            return ["songbook/home_strumsphere.html"]
        elif site_name == "Uke4ia":
            return ["songbook/home_uke4ia.html"]
        return ["songbook/home_francouke.html"]


class ArtistListView(SiteContextMixin, ListView):
    """
    Public list of artists for the current site.
    """
    template_name = "songbook/artist_list.html"
    context_object_name = "artists"

    def get_queryset(self):
        site_name = self.get_site_name()
        queryset = Song.objects.filter(site_name=site_name).values_list("metadata__artist", flat=True).distinct()
        # ensure letter filtering still works if provided
        selected_letter = self.kwargs.get("letter", None)
        artists = [a for a in queryset if a]
        if selected_letter:
            artists = [a for a in artists if a and a.upper().startswith(selected_letter.upper())]
        return sorted(artists)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_artists = self.get_queryset()
        first_letters = sorted({a[0].upper() for a in all_artists if a})
        context.update({
            "first_letters": first_letters,
            "selected_letter": self.kwargs.get("letter", None),
            "artist_columns": [all_artists[i::4] for i in range(4)],
        })
        return context


class UserSongListView(ListView):
    """
    Songs contributed by a particular user (site_name must be passed in URL).
    """
    model = Song
    template_name = "songbook/user_songs.html"
    context_object_name = "songs"
    ordering = ["songTitle"]
    paginate_by = 15

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        site_name = self.kwargs.get("site_name")
        return Song.objects.filter(contributor=user, site_name=site_name).order_by("songTitle")


class ScoreView(DetailView):
    """
    Public song score/detail view.
    Preferences are included in context if the user is authenticated.
    """
    model = Song
    template_name = "songbook/song_simplescore.html"
    context_object_name = "score"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["song"] = self.get_object()

        if self.request.user.is_authenticated:
            preferences, created = None, False
            try:
                from users.models import UserPreference
                preferences, created = UserPreference.objects.get_or_create(user=self.request.user)
            except Exception:
                preferences = None
            context["preferences"] = preferences
        else:
            context["preferences"] = None

        context.update(site_context(self.request))
        return context


class SongListView(SiteContextMixin, ListView):
    """
    Public paginated list of songs for the current site, with filtering/search.
    """
    model = Song
    template_name = "songbook/song_list.html"
    context_object_name = "songs"
    ordering = ["songTitle"]
    paginate_by = 25

    # Allow anonymous users to browse; we removed the forced auth modal.
    def get_queryset(self):
        queryset = super().get_queryset()
        site_name = self.get_site_name()
        queryset = queryset.filter(site_name=site_name)

        # Filter by whether formatted exists
        if self.request.GET.get("formatted") == "1":
            queryset = queryset.filter(songformatting__isnull=False)

        search_query = self.request.GET.get("q", "")
        selected_tag = self.request.GET.get("tag", "")
        artist_name = self.kwargs.get("artist_name")

        if search_query:
            queryset = queryset.filter(
                Q(songTitle__icontains=search_query)
                | Q(metadata__artist__icontains=search_query)
                | Q(metadata__songwriter__icontains=search_query)
            )

        if selected_tag:
            queryset = queryset.filter(tags__name=selected_tag)

        if artist_name:
            queryset = queryset.filter(metadata__artist__iexact=artist_name)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_name = self.get_site_name()
        context["selected_artist"] = self.kwargs.get("artist_name")
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_tag"] = self.request.GET.get("tag", "")

        site_songs = Song.objects.filter(site_name=site_name)
        all_tags = Tag.objects.filter(song__in=site_songs).distinct().values_list("name", flat=True)
        context["all_tags"] = all_tags

        # Build song_data list once for the page (avoid DB + heavy ops in template)
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
        context.update(site_context(self.request))
        return context

# songbook/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Song

@csrf_exempt
def set_scroll_speed(request, song_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            song = Song.objects.get(pk=song_id)
            song.scroll_speed = data.get("scroll_speed", song.scroll_speed)
            song.save(update_fields=["scroll_speed"])
            return JsonResponse({"status": "ok", "scroll_speed": song.scroll_speed})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=405)


# songbook/views.py
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@require_POST
@csrf_exempt  # or use @csrf_protect + pass CSRF token via JS
def update_scroll_speed(request, song_id):
    try:
        data = json.loads(request.body.decode("utf-8"))
        new_speed = int(data.get("scroll_speed", 30))
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid data"}, status=400)

    song = get_object_or_404(Song, pk=song_id)
    song.scroll_speed = new_speed
    song.save(update_fields=["scroll_speed"])

    return JsonResponse({"status": "ok", "new_speed": new_speed})


class SongCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new song. Contributor is automatically set to the current user.
    """
    model = Song
    fields = ["songTitle", "songChordPro", "metadata", "tags", "acknowledgement"]

    def form_valid(self, form):
        form.instance.contributor = self.request.user
        context_data = site_context(self.request)
        form.instance.site_name = context_data.get("site_name")

        # parse and store lyrics_with_chords if possible
        raw = form.cleaned_data.get("songChordPro", "")
        try:
            parsed = parse_song_data(raw) if raw else ""
        except Exception as e:
            form.add_error("songChordPro", f"Error parsing song data: {e}")
            return self.form_invalid(form)
        form.instance.lyrics_with_chords = parsed
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site_context(self.request))
        return context

    def get_success_url(self):
        site_name = getattr(self.object, "site_name", None) or site_context(self.request).get("site_name")
        return reverse(f"{site_name.lower()}:score_view", kwargs={"pk": self.object.pk})




class SongUpdateView(LoginRequiredMixin, ContributorOrAdminMixin, UpdateView):
    """
    Update a song. Only the contributor or staff can update.
    """
    model = Song
    fields = ["songTitle", "songChordPro", "lyrics_with_chords", "metadata", "tags", "acknowledgement"]

    def form_valid(self, form):
        # keep contributor the same (or set to current user for safety)
        form.instance.contributor = self.request.user
        raw_lyrics = form.cleaned_data.get("songChordPro", "")
        try:
            parsed_lyrics = parse_song_data(raw_lyrics) if raw_lyrics else ""
        except Exception as e:
            form.add_error("songChordPro", f"Error parsing song data: {e}")
            return self.form_invalid(form)
        form.instance.lyrics_with_chords = parsed_lyrics
        return super().form_valid(form)

    def get_success_url(self):
        site_name = getattr(self.object, "site_name", None) or site_context(self.request).get("site_name")
        return reverse(f"{site_name.lower()}:score_view", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site_context(self.request))
        return context


class SongDeleteView(LoginRequiredMixin, ContributorOrAdminMixin, DeleteView):
    """
    Delete a song. Only the contributor or staff can delete.
    """
    model = Song
    success_url = reverse_lazy("songbook-home")


