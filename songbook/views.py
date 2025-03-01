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

# Import project-specific modules
from .models import Song, SongFormatting
from .forms import SongForm, TagFilterForm, SongFormattingForm
from .parsers import parse_song_data
from .utils.transposer import extract_chords, transpose_lyrics
from songbook.utils.pdf_generator import generate_songs_pdf, load_chords
from songbook.utils.ABC2audio import convert_abc_to_audio
from users.models import UserPreference
import urllib.parse
import logging

logger = logging.getLogger(__name__)

@login_required
@permission_required("songbook.change_songformatting", raise_exception=True)
def edit_song_formatting(request, song_id):
    """Edit song formatting with a fallback to Gaulind's settings if needed."""
    
    # Try to get user's formatting, or use Gaulind's as fallback
    formatting, created = SongFormatting.objects.get_or_create(
        user=request.user, song_id=song_id,
        defaults={'intro': None, 'verse': None, 'chorus': None, 'bridge': None, 'interlude': None, 'outro': None}
    )

    if created:
        gaulind_formatting = SongFormatting.objects.filter(user__username="Gaulind", song_id=song_id).first()
        if gaulind_formatting:
            formatting.intro = gaulind_formatting.intro
            formatting.verse = gaulind_formatting.verse
            formatting.chorus = gaulind_formatting.chorus
            formatting.bridge = gaulind_formatting.bridge
            formatting.interlude = gaulind_formatting.interlude
            formatting.outro = gaulind_formatting.outro
            formatting.save()

    # Process the form
    if request.method == "POST":
        form = SongFormattingForm(request.POST, instance=formatting)
        if form.is_valid():
            form.save()
            messages.success(request, "Formatting updated successfully!")
            return redirect("score", pk=song_id)
    else:
        form = SongFormattingForm(instance=formatting)

    return render(request, "songbook/edit_formatting.html", {"form": form, "pk": song_id})

class ArtistListView(LoginRequiredMixin, ListView):
    template_name = "songbook/artist_list.html"
    context_object_name = "artists"
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, "users/auth_modal.html", {"next_url": request.path})
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Get unique artists and filter by first letter if provided.
        """
        queryset = (
            Song.objects.exclude(metadata__artist__isnull=True)
            .exclude(metadata__artist="")
            .annotate(artist_name=Lower(Cast("metadata__artist", CharField())))
            .values_list("metadata__artist", flat=True)
            .distinct()
            .order_by("artist_name")
        )

        # Get the letter from the URL if filtering by letter
        letter = self.kwargs.get("letter")
        
        if letter:
            # ✅ Ensure None values are filtered out before accessing the first character
            queryset = [artist for artist in queryset if artist and artist[0].upper() == letter.upper()]

        return queryset


    def get_context_data(self, **kwargs):
        """Ensure letter navigation is always visible."""
        context = super().get_context_data(**kwargs)

        # ✅ Get all unique artist names (not just filtered ones)
        all_artists = (
            Song.objects.exclude(metadata__artist__isnull=True)
            .exclude(metadata__artist="")
            .annotate(artist_name=Lower(Cast("metadata__artist", CharField())))
            .values_list("metadata__artist", flat=True)
            .distinct()
        )

        # ✅ Extract all first letters from all artists
        first_letters = sorted(set(artist[0].upper() for artist in all_artists if artist))

        # ✅ Ensure filtered artists are shown correctly
        letter = self.kwargs.get("letter")
        if letter:
            filtered_artists = [artist for artist in all_artists if artist and artist[0].upper() == letter.upper()]
        else:
            filtered_artists = list(all_artists)  # Show all artists if no letter selected

        # ✅ Split into columns (max 20 per column)
        artists_per_column = 20
        artist_columns = [filtered_artists[i:i + artists_per_column] for i in range(0, len(filtered_artists), artists_per_column)]

        context["artist_columns"] = artist_columns  # ✅ Keep artists split into columns
        context["first_letters"] = first_letters  # ✅ Ensure letters always appear
        context["selected_letter"] = letter  # ✅ Track selected letter

        # ✅ Debugging print (Check this in PythonAnywhere error logs)
        print("DEBUG: First Letters Passed to Template:", first_letters)

        return context



def preview_pdf(request, song_id):
    """Generate a transposed PDF with user-defined font sizes stored in JSON fields."""
    song = get_object_or_404(Song, pk=song_id)
    user = request.user

    existing_formatting = SongFormatting.objects.filter(user=user, song=song).exists()
    formatting = SongFormatting.objects.filter(user=user, song=song).first()

    if not formatting:
        # 🚀 If no formatting exists for the user, use Gaulind’s formatting as the default
        formatting = SongFormatting.objects.filter(user__username="Gaulind", song=song).first()

    after_retrieval_formatting = SongFormatting.objects.filter(user=user, song=song).exists()
    transpose_value = int(request.GET.get("transpose", 0))
    
    # Transpose the song if needed
    if transpose_value != 0:
        song.lyrics_with_chords = transpose_lyrics(song.lyrics_with_chords, transpose_value)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{song.songTitle}_preview.pdf"'

    generate_songs_pdf(response, [song], user, transpose_value, formatting)  
    return response



import logging

logger = logging.getLogger(__name__)


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
    """Generates a PDF for a single song."""
    song = get_object_or_404(Song, pk=song_id)
    
    return generate_pdf_response(song.songTitle, [song], request.user)

def get_chord_definition(request, chord_name):
    """
    Django view to fetch the definition of a specific chord.
    """
    chords = load_chords()
    for chord in chords:
        if chord["name"].lower() == chord_name.lower():
            return JsonResponse({"success": True, "chord": chord})
    return JsonResponse({"success": False, "error": f"Chord '{chord_name}' not found."})

def chord_dictionary(request):
    instruments = ["ukulele", "guitar", "mandolin", "banjo", "baritone_ukulele"]
    chord_data = {instrument: load_chords(instrument) for instrument in instruments}
    return render(request, "songbook/allChordsTable.html", {"chord_data": chord_data})

from django.shortcuts import render


def home(request):
    context = {
        'songs':Song.objects.all()
    }
    return render(request, 'songbook/home.html',context)

class SongListView(ListView):
    model = Song
    template_name = 'songbook/song_list.html'
    context_object_name = 'songs'
    ordering = ['songTitle']
    paginate_by = 25

    def dispatch(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                return render(request, "users/auth_modal.html", {"next_url": request.path})
            return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Override to filter the song queryset based on search query and tag.
        """
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '')  # Search query
        selected_tag = self.request.GET.get('tag', '')  # Selected tag
        artist_name = self.kwargs.get('artist_name')  # Get artist from URL

        # Apply filters
        if search_query:
            queryset = queryset.filter(
                Q(songTitle__icontains=search_query) |
                Q(metadata__artist__icontains=search_query) |
                Q(metadata__songwriter__icontains=search_query)
            )

        if selected_tag:  # Filter by tag if a tag is selected
            queryset = queryset.filter(tags__name=selected_tag)

        if artist_name:
            queryset = queryset.filter(metadata__artist__iexact=artist_name)  # ✅ No need to decode

        return queryset


    def post(self, request, *args, **kwargs):
        tag_id = request.POST.get('tag')
        if tag_id:
            return redirect(reverse('generate_titles_pdf') + f'?tag={tag_id}')
        return self.get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        """
        Add filtered song data, chords, and tags to the template context.
        """
        context = super().get_context_data(**kwargs)
        context['selected_artist'] = self.kwargs.get('artist_name')
        search_query = self.request.GET.get('q', '')
        selected_tag = self.request.GET.get('tag', '')  # Selected tag
        song_data = []

        # Build song data with chords and tags
        for song in context['songs']:
            parsed_data = song.lyrics_with_chords or ""
            chords = extract_chords(parsed_data, unique=True) if parsed_data else []
            tags = [tag.name for tag in song.tags.all()]  # Get tags for each song
            song_data.append({
                'song': song,
                'chords': ', '.join(chords),
                'tags': ', '.join(tags),
            })

        # Fetch all unique tags and add them to the context
        all_tags = Tag.objects.all().values_list('name', flat=True).distinct()

        context['song_data'] = song_data
        context['search_query'] = search_query
        context['selected_tag'] = selected_tag  # Pass the selected tag
        context['all_tags'] = all_tags  # Add all tags to context
        return context
    
class UserSongListView (ListView):
    model = Song
    template_name = 'songbook/user_songs.html'
    context_object_name = 'songs'
    ordering = ['songTitle']
    paginate_by = 15

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Song.objects.filter(contributor=user).order_by('songTitle')


#This is second column of home.html
class ScoreView(LoginRequiredMixin, DetailView):
    model = Song
    template_name = 'songbook/song_simplescore.html'
    context_object_name = 'score'
    login_url = "/users/login/"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

                # Fetch the user's preferences
        if self.request.user.is_authenticated:
            preferences, created = UserPreference.objects.get_or_create(user=self.request.user)
            context["preferences"] = preferences
        else:
            context["preferences"] = None  # Handle unauthenticated users if necessary
        
        return context

class SongCreateView(LoginRequiredMixin, CreateView):
    model = Song
    fields = ['songTitle','songChordPro','metadata','tags','acknowledgement']
    def form_valid(self, form):
        form.instance.contributor = self.request.user
        return super().form_valid(form)

class SongUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Song
    fields = ['songTitle', 'songChordPro', 'lyrics_with_chords', 'metadata','tags','acknowledgement']
    #success_url = reverse_lazy('songbook-home')  # Redirect after success

    def get_success_url(self):
        # Redirect to the updated song's detail page
        return reverse('score', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # Assign the contributor to the current user
        form.instance.contributor = self.request.user
        
        # Parse the songChordPro field
        raw_lyrics = form.cleaned_data['songChordPro']
        try:
            # Attempt to parse the songChordPro data
            parsed_lyrics = parse_song_data(raw_lyrics)
        except Exception as e:
            # Handle errors in parsing gracefully
            form.add_error('songChordPro', f"Error parsing song data: {e}")
            return self.form_invalid(form)
        
        # Update the lyrics_with_chords field with parsed data
        form.instance.lyrics_with_chords = parsed_lyrics
        return super().form_valid(form)


    def test_func(self):
        return self.request.user.is_authenticated

    def get_object(self, queryset=None):
        return super().get_object(queryset)


class SongDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Song
    success_url = reverse_lazy('songbook-home')  # Use reverse_lazy for better practice.

    def test_func(self):
        song = self.get_object()
        return self.request.user == song.contributor


def about(request):
    return render (request, 'songbook/about.html',{'title':about})

def betabugs(request):
    return render (request, 'songbook/betabugs.html',{'title':betabugs})