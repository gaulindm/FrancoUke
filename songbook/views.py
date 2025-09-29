from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.functions import Lower
from django.db.models import CharField
from django.db.models.functions import Cast
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from taggit.models import Tag
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from collections import defaultdict
from django.core.exceptions import PermissionDenied
from .mixins import SiteContextMixin
# Import project-specific modules
from .models import Song, SongFormatting
from .forms import SongForm, TagFilterForm, SongFormattingForm
from .parsers import parse_song_data
from songbook.utils.transposer import extract_chords, transpose_lyrics
from songbook.utils.pdf_generator import generate_songs_pdf, load_chords
from songbook.context_processors import site_context
from songbook.utils.ABC2audio import convert_abc_to_audio
from users.models import UserPreference
import urllib.parse
import logging

from .context_processors import site_context

@login_required
@permission_required("songbook.change_songformatting", raise_exception=True)
def edit_song_formatting(request, song_id):
    """Edit song formatting with Dual Edition support."""
    context_data = site_context(request)
    site_name = context_data["site_name"]

    formatting, created = SongFormatting.objects.get_or_create(
        user=request.user, song_id=song_id,
        defaults={'intro': {}, 'verse': {}, 'chorus': {}, 'bridge': {}, 'interlude': {}, 'outro': {}}
    )

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

    return render(request, "songbook/edit_formatting.html", {
        "form": form,
        "pk": song_id,
        "formatting": formatting,
        **context_data,  # adds site_name, base_template, site_namespace
    })


class ArtistListView(SiteContextMixin, ListView):
    template_name = "songbook/artist_list.html"
    context_object_name = "artists"

    def get_queryset(self):
        site_name = self.get_site_name()
        queryset = Song.objects.filter(site_name=site_name).values_list(
            "metadata__artist", flat=True
        ).distinct()

        # Filter by letter if provided
        self.selected_letter = self.kwargs.get("letter")
        if self.selected_letter:
            queryset = [a for a in queryset if a and a.upper().startswith(self.selected_letter.upper())]

        return sorted(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_artists = self.get_queryset()
        first_letters = sorted({a[0].upper() for a in all_artists if a})

        # ✅ Extra artist context
        context.update({
            "first_letters": first_letters,
            "selected_letter": self.selected_letter,
            "artist_columns": [
                all_artists[i::4] for i in range(4)  # 4 columns layout
            ],
        })
        return context



from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Song
from songbook.utils.transposer import transpose_chord # <- assuming this exists

from django.http import HttpResponse


def preview_pdf(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    user = request.user

    transpose_value = int(request.GET.get("transpose", 0))
    if transpose_value != 0:
        song.lyrics_with_chords = transpose_lyrics(song.lyrics_with_chords, transpose_value)

    context_data = site_context(request)
    site_name = context_data["site_name"]

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{song.songTitle}_preview.pdf"'
    generate_songs_pdf(response, [song], user, transpose_value, None, site_name=site_name)
    return response




import logging

logger = logging.getLogger(__name__)

#For the action button
def generate_pdf_response(filename, songs, user=None):
    """Reusable function to generate and return a PDF response."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    generate_songs_pdf(response, songs, user)
    return response


def generate_multi_song_pdf(request):
    """Generates a PDF for multiple songs filtered by tag."""
    tag_name = request.POST.get('tag_name', '').strip()
    songs = Song.objects.filter(tags__name=tag_name) if tag_name else Song.objects.none()

    return generate_pdf_response("multi_song_report", songs, request.user)


@login_required
def generate_single_song_pdf(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    user = request.user

    context_data = site_context(request)
    site_name = context_data["site_name"]

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{song.songTitle}.pdf"'
    generate_songs_pdf(response, [song], user, transpose_value=0, formatting=None, site_name=site_name)
    return response


def get_chord_definition(request, chord_name):
    """
    Django view to fetch the definition of a specific chord.
    """
    chords = load_chords()
    for chord in chords:
        if chord["name"].lower() == chord_name.lower():
            return JsonResponse({"success": True, "chord": chord})
    return JsonResponse({"success": False, "error": f"Chord '{chord_name}' not found."})

from django.shortcuts import render

def chord_dictionary(request):
    context_data = site_context(request)
    return render(request, "songbook/chord_dictionary.html", context_data)



def home(request, site_name):
    return render(request, 'index.html', {'site_name': site_name})

from django.views.generic import ListView
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Q
from taggit.models import Tag

from songbook.models import Song, SongFormatting
from songbook.utils.transposer import extract_chords

from django.views.generic import TemplateView

class LandingView(TemplateView):
    def get_template_names(self):
        context_data = site_context(self.request)
        site_name = context_data["site_name"]

        if site_name == "StrumSphere":
            return ["songbook/home_strumsphere.html"]
        elif site_name == "Uke4ia":
            return ["songbook/home_uke4ia.html"]
        return ["songbook/home_francouke.html"]


class UserSongListView(ListView):
    model = Song
    template_name = 'songbook/user_songs.html'
    context_object_name = 'songs'
    ordering = ['songTitle']
    paginate_by = 15

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        site_name = self.kwargs.get('site_name')  # Get site name from URL
        return Song.objects.filter(contributor=user, site_name=site_name).order_by('songTitle')


#This is second column of home.html
class ScoreView(LoginRequiredMixin, DetailView):
    model = Song
    template_name = 'songbook/song_simplescore.html'
    context_object_name = 'score'
    login_url = "/users/login/"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ✅ song object already available as "score" (context_object_name),
        # but you can keep this alias if templates expect "song"
        context['song'] = self.get_object()

        # ✅ Fetch user preferences if logged in
        if self.request.user.is_authenticated:
            preferences, created = UserPreference.objects.get_or_create(user=self.request.user)
            context["preferences"] = preferences
        else:
            context["preferences"] = None

        return context

from .mixins import SiteContextMixin  # Make sure this is imported

class SongListView(SiteContextMixin, ListView):
    model = Song
    template_name = 'songbook/song_list.html'
    context_object_name = 'songs'
    ordering = ['songTitle']
    paginate_by = 25

    def dispatch(self, request, *args, **kwargs):
        # Optional: show auth modal if not logged in
        if not request.user.is_authenticated:
            return render(request, "users/auth_modal.html", {"next_url": request.path})
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        site_name = self.get_site_name()  # From the mixin
        queryset = queryset.filter(site_name=site_name)

        # Filters
        if self.request.GET.get("formatted") == "1":
            queryset = queryset.filter(songformatting__isnull=False)

        search_query = self.request.GET.get('q', '')
        selected_tag = self.request.GET.get('tag', '')
        artist_name = self.kwargs.get('artist_name')

        if search_query:
            queryset = queryset.filter(
                Q(songTitle__icontains=search_query) |
                Q(metadata__artist__icontains=search_query) |
                Q(metadata__songwriter__icontains=search_query)
            )

        if selected_tag:
            queryset = queryset.filter(tags__name=selected_tag)

        if artist_name:
            queryset = queryset.filter(metadata__artist__iexact=artist_name)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        site_name = self.get_site_name()  # From mixin
        context['selected_artist'] = self.kwargs.get('artist_name')
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_tag'] = self.request.GET.get('tag', '')

        # Tags for the current site
        site_songs = Song.objects.filter(site_name=site_name)
        all_tags = Tag.objects.filter(song__in=site_songs).distinct().values_list('name', flat=True)
        context['all_tags'] = all_tags

        # Song parsing
        song_data = []
        for song in context['songs']:
            parsed_data = song.lyrics_with_chords or ""
            chords = extract_chords(parsed_data, unique=True) if parsed_data else []
            tags = [tag.name for tag in song.tags.all()]
            is_formatted = SongFormatting.objects.filter(song=song).exists()

            song_data.append({
                'song': song,
                'chords': ', '.join(chords),
                'tags': ', '.join(tags),
                'is_formatted': is_formatted,
            })

        context['song_data'] = song_data
        return context

class SongCreateView(LoginRequiredMixin, CreateView):
    model = Song
    fields = ['songTitle', 'songChordPro', 'metadata', 'tags', 'acknowledgement']

    def form_valid(self, form):
        form.instance.contributor = self.request.user
        context_data = site_context(self.request)
        form.instance.site_name = context_data["site_name"]
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site_context(self.request))
        return context

    def get_success_url(self):
        return reverse("songbook:song_list")

class SongUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Song
    fields = ['songTitle', 'songChordPro', 'lyrics_with_chords', 'metadata', 'tags', 'acknowledgement']

    def get_success_url(self):
        site_name = self.object.site_name or site_context(self.request)["site_name"]
        return reverse(f"{site_name.lower()}:score_view", kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.contributor = self.request.user
        raw_lyrics = form.cleaned_data['songChordPro']
        try:
            parsed_lyrics = parse_song_data(raw_lyrics)
        except Exception as e:
            form.add_error('songChordPro', f"Error parsing song data: {e}")
            return self.form_invalid(form)
        form.instance.lyrics_with_chords = parsed_lyrics
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site_context(self.request))
        return context


class SongDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Song
    success_url = reverse_lazy('songbook-home')  # Use reverse_lazy for better practice.

    def test_func(self):
        song = self.get_object()
        return self.request.user == song.contributor

def about(request):
    return render(request, "songbook/about.html", site_context(request))

def whats_new(request):
    return render(request, "songbook/whats_new.html", site_context(request))
