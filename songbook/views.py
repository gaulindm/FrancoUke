
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin,  UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView, 
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    )
from .models import Song
from django.views import View
from django.db. models import Prefetch
from .parsers import parse_song_data
from .utils.transposer import extract_chords, calculate_steps, transpose_lyrics, detect_key
from unidecode import unidecode
from django.http import HttpResponse
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import letter
from django.db.models import Q  # Import Q for complex queries
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from .models import Song, SongFormatting  # Adjust based on your models
from taggit.models import Tag
from songbook.utils.pdf_generator import generate_songs_pdf  # Import the utility function
from django.http import JsonResponse
from songbook.utils.pdf_generator import load_chords
from users.models import UserPreference  # Replace `user` with the actual app name if different
from songbook.utils.ABC2audio import convert_abc_to_audio
from django.contrib.auth.decorators import login_required, permission_required
from .models import SongFormatting
from .forms import SongFormattingForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SongForm, TagFilterForm
from songbook.models import Song
from django.utils.timezone import now
from django.contrib.auth.models import User
import re


from django.http import HttpResponse
from .utils.pdf_generator import generate_songs_pdf
from .utils.transposer import transpose_lyrics  # Import your transposer function

@login_required
@permission_required("songbook.change_songformatting", raise_exception=True)
def edit_song_formatting(request, song_id):
    
    # ✅ Try to get the user's formatting
    formatting = SongFormatting.objects.filter(user=request.user, song_id=song_id).first()

    if not formatting:
        # 🚀 If the user has no formatting, check if Gaulind has one
        gaulind_formatting = SongFormatting.objects.filter(user__username="Gaulind", song_id=song_id).first()

        if gaulind_formatting:
            print(f"DEBUG: Creating formatting for {request.user.username} based on Gaulind's settings.")

            # ✅ Create a new formatting entry for the user based on Gaulind's settings
            formatting = SongFormatting.objects.create(
                user=request.user,
                song_id=song_id,
                intro=gaulind_formatting.intro,
                verse=gaulind_formatting.verse,
                chorus=gaulind_formatting.chorus,
                bridge=gaulind_formatting.bridge,
                interlude=gaulind_formatting.interlude,
                outro=gaulind_formatting.outro,
            )
        else:
            print(f"DEBUG: No formatting found for Gaulind. Creating an empty formatting entry for {request.user.username}.")
            formatting = SongFormatting.objects.create(user=request.user, song_id=song_id)

    # ✅ Now formatting is guaranteed to exist, so we can proceed normally
    if request.method == "POST":
        form = SongFormattingForm(request.POST, instance=formatting)
        if form.is_valid():
            form.save()
            messages.success(request, "Formatting updated successfully!")
            return redirect("score", pk=song_id)
    else:
        form = SongFormattingForm(instance=formatting)

    return render(request, "songbook/edit_formatting.html", {"form": form, "pk": song_id})





    # 🔍 Debugging - Check if song_id is empty or None
    print(f"DEBUG: song_id before passing to template: {song_id}")

    if not song_id:  # ✅ If song_id is missing, prevent a crash
        messages.error(request, "Song ID is missing.")
        return redirect("songbook-home")  # Redirect to home if song_id is invalid

    if request.method == "POST":
        form = SongFormattingForm(request.POST, instance=formatting)
        if form.is_valid():
            form.save()
            messages.success(request, "Formatting updated successfully!")
            print(f"DEBUG: Redirecting to score with pk={song_id}")  # ✅ Debugging
            return redirect("score", pk=song_id)  # ✅ Fix redirect

    else:
        form = SongFormattingForm(instance=formatting)

    return render(request, "songbook/edit_formatting.html", {"form": form, "pk": song_id})


def preview_pdf(request, song_id):
    """Generate a transposed PDF with user-defined font sizes stored in JSON fields."""
    song = get_object_or_404(Song, pk=song_id)
    user = request.user

    # ✅ Debug: Check existing formatting before retrieving
    existing_formatting = SongFormatting.objects.filter(user=user, song=song).exists()
    print(f"DEBUG: Before retrieval - Formatting exists for {user.username}? {existing_formatting}")

    # ✅ Try to get the logged-in user's formatting without creating a new one
    formatting = SongFormatting.objects.filter(user=user, song=song).first()

    if not formatting:
        print(f"DEBUG: No formatting found for {user.username}, trying Gaulind's formatting.")
        # 🚀 If no formatting exists for the user, use Gaulind’s formatting as the default
        formatting = SongFormatting.objects.filter(user__username="Gaulind", song=song).first()

    # ✅ Debug: Confirm what formatting is being used
    if formatting:
        print(f"DEBUG: Using formatting from user {formatting.user.username}")
    else:
        print("DEBUG: No formatting found for preview.")

    # ✅ Debug: Check if a new entry appears after preview
    after_retrieval_formatting = SongFormatting.objects.filter(user=user, song=song).exists()
    print(f"DEBUG: After retrieval - Formatting exists for {user.username}? {after_retrieval_formatting}")

    # ✅ Get transpose value (default to 0)
    transpose_value = int(request.GET.get("transpose", 0))
    
    # Transpose the song if needed
    if transpose_value != 0:
        song.lyrics_with_chords = transpose_lyrics(song.lyrics_with_chords, transpose_value)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{song.songTitle}_preview.pdf"'

    generate_songs_pdf(response, [song], user, transpose_value, formatting)  
    return response






def song_list(request):
    form = TagFilterForm(request.POST or None)
    songs = Song.objects.all()

    if request.method == 'POST' and form.is_valid():
        selected_tag = form.cleaned_data['tag']
        songs = songs.filter(tags=selected_tag)

    context = {
        'songs': songs,
        'form': form,
    }
    return render(request, 'song_list.html', context)



import logging

logger = logging.getLogger(__name__)

def generate_titles_pdf(request):
    tag_name = request.POST.get('tag_name')  # Retrieve the tag name from POST
    if tag_name:
        try:
            tag = Tag.objects.get(name=tag_name)  # Look up by name instead of ID
            songs = Song.objects.filter(tags=tag)
        except Tag.DoesNotExist:
            songs = Song.objects.none()
    else:
        songs = Song.objects.none()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="song_titles.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [Paragraph("List of Songs", styles['Title']), Spacer(1, 12)]

    for song in songs:
        elements.append(Paragraph(song.songTitle, styles['Normal']))
        elements.append(Spacer(1, 12))

    doc.build(elements)
    return response


def generate_multi_song_pdf(request):
    tag_name = request.POST.get('tag_name')
    if tag_name:
        try:
            tag = Tag.objects.get(name=tag_name)
            songs = Song.objects.filter(tags=tag)
        except Tag.DoesNotExist:
            songs = Song.objects.none()
    else:
        songs = Song.objects.none()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="multi_song_report.pdf"'

    generate_songs_pdf(response, songs, request.user)
    return response





def generate_audio_from_abc(request, song_id):
    song = Song.objects.get(pk=song_id)
    if not song.abc_notation:
        return HttpResponse("No ABC notation available for this song.", status=400)

    audio_path = convert_abc_to_audio(song.abc_notation)
    with open(audio_path, "rb") as audio_file:
        response = HttpResponse(audio_file.read(), content_type="audio/wav")
        response["Content-Disposition"] = f'inline; filename="{song.title}_melody.wav"'
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


def chord_dictionary(request):
    instruments = ["ukulele", "guitar", "mandolin", "banjo", "baritone_ukulele"]
    chord_data = {instrument: load_chords(instrument) for instrument in instruments}
    return render(request, "songbook/allChordsTable.html", {"chord_data": chord_data})

from django.shortcuts import render




@login_required
def generate_single_song_pdf(request, song_id):
    from django.http import HttpResponse
    from .models import Song
    from .utils.pdf_generator import generate_songs_pdf

    # Fetch the song and user
    song = Song.objects.get(pk=song_id)
    user = request.user

    # Fetch the user's instrument preference
    #try:
    #    instrument = user.userpreference.instrument
    #except UserPreference.DoesNotExist:
    #    instrument = 'ukulele'  # Default to ukulele if no preference is set


    # Prepare the response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{song.songTitle}.pdf"'

    # Generate the PDF
    generate_songs_pdf(response, [song], user)
    return response



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

    def get_queryset(self):
        """
        Override to filter the song queryset based on search query and tag.
        """
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '')  # Search query
        selected_tag = self.request.GET.get('tag', '')  # Selected tag

        # Apply filters
        if search_query:
            queryset = queryset.filter(
                Q(songTitle__icontains=search_query) |
                Q(metadata__artist__icontains=search_query) |
                Q(metadata__composer__icontains=search_query) |
                Q(metadata__lyricist__icontains=search_query)
            )

        if selected_tag:  # Filter by tag if a tag is selected
            queryset = queryset.filter(tags__name=selected_tag)

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
class ScoreView(DetailView):
    model = Song
    template_name = 'songbook/song_simplescore.html'  # Temporary template for experiments 
    context_object_name = 'score'

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
    success_url = reverse_lazy('songbook-home')  # Redirect after success

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
#If user needs to be contributor
#  def test_func(self):
#       song = self.get_object()
#       if self.request.user == song.contributor:
#           return True
#       return False 

#   def get_object(self, queryset=None):
#       # Ensure only the contributor can update the song
#       obj = super().get_object(queryset)
#       if obj.contributor != self.request.user:
#           raise PermissionDenied("You do not have permission to edit this song.")
#       return obj

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