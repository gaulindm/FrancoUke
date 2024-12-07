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
from .transposer import extract_chords, calculate_steps, transpose_lyrics, detect_key
from unidecode import unidecode
import svgwrite
from django.http import HttpResponse

def chord_diagram_view(request):
    # Create an SVG diagram
    dwg = svgwrite.Drawing(size=("100px", "100px"))
    dwg.add(dwg.line((10, 10), (90, 90), stroke=svgwrite.rgb(10, 10, 16, '%')))
    dwg.add(dwg.text("Chord Diagram", insert=(10, 20), fill="black"))

    # Return as SVG response
    response = HttpResponse(dwg.tostring(), content_type="image/svg+xml")
    return response


class ChordDiagramsView(View):
    template_name = 'songbook/chord_diagrams_view.html'

    def get(self, request, chords, *args, **kwargs):
        # Split the comma-separated chords passed in the path
        chords_list = chords.split(',')
        context = {'chords': chords_list}
        return render(request, self.template_name, context)

#def score_view(request, song_id):
#    song = get_object_or_404(Song, id=song_id)  # Fetch the song based on the id
#    return render(request, 'score.html', {'score': song})  

def song_with_chords_view(request, song_id, new_key, instrument='ukulele'):
    # Data for the left side (transposed song)
    song = get_object_or_404(Song, id=song_id)
    parsed_data = song.lyrics_with_chords  # Assuming this is parsed and stored
    original_key = song.metadata.get('key') or detect_key(parsed_data)
    steps = calculate_steps(original_key, new_key)
    transposed_lyrics = transpose_lyrics(parsed_data, steps)

    # Data for the right side (chord diagrams)
    chords_param = request.GET.get('chords', '')  # Optional: Pass chords via query params
    desired_chords = chords_param.split(',') if chords_param else []
    is_lefty = request.GET.get('isLefty', 'false').lower() == 'true'

    # Fetch chords for the instrument
    chords_queryset = Chord.objects.filter(
        instrument__name=instrument,
        name__in=desired_chords
    ) if desired_chords else Chord.objects.filter(instrument__name=instrument)

    chords = []
    for chord in chords_queryset:
        frets = chord.frets[::-1] if is_lefty else chord.frets
        fingers = chord.fingers[::-1] if is_lefty and chord.fingers else chord.fingers
        chords.append({
            "name": chord.name,
            "frets": frets,
            "fingers": fingers,
            "svg": generate_chord_svg(
                chord_name=chord.name,
                frets=frets,
                fingers=fingers
            )
        })

    context = {
        'score': song,
        'transposed_lyrics': transposed_lyrics,
        'chords': chords,
        'instrument': instrument,
        'isLefty': is_lefty,
    }
    return render(request, 'songbook/song_with_chords.html', context)


def home(request):
    context = {
        'songs':Song.objects.all()
    }
    return render(request, 'songbook/home.html',context)

class SongListView (ListView):
    model = Song
    template_name = 'songbook/home.html'
    context_object_name = 'songs'
    ordering = ['songTitle']
    paginate_by = 15

    def get_queryset(self):
        # Sort by title and return
        return Song.objects.all()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        song_data = []

        for song in context['songs']:
            parsed_data = song.lyrics_with_chords  # Assuming this is already parsed and stored
            chords = extract_chords(parsed_data,unique=True)
            song_data.append({
                'song': song,
                'chords': ', '.join(chords)  # Join chords into a string for display
            })

        context['song_data'] = song_data
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

#This is the view that works well in first column of home.html
class ScoreView(DetailView):
    model = Song
    template_name = 'songbook/song_simplescore.html' 
    context_object_name = 'score'

#This is second column of home.html
class NewScoreView(DetailView):
    model = Song
    template_name = 'songbook/new_score_view.html'  # Temporary template for experiments 
    context_object_name = 'score'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add custom context data for experimentation
        context['experiment'] = "This is a test for the new score view"
        return context    


class SongCreateView(LoginRequiredMixin, CreateView):
    model = Song
    fields = ['songTitle','songChordPro','metadata']
    def form_valid(self, form):
        form.instance.contributor = self.request.user
        return super().form_valid(form)

class SongUpdateView(LoginRequiredMixin, UpdateView):
    model = Song
    fields = ['songTitle', 'songChordPro', 'lyrics_with_chords', 'metadata']
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

    def get_object(self, queryset=None):
        # Ensure only the contributor can update the song
        obj = super().get_object(queryset)
        if obj.contributor != self.request.user:
            raise PermissionDenied("You do not have permission to edit this song.")
        return obj




class SongDeleteView (LoginRequiredMixin, UserPassesTestMixin,DeleteView):
    model = Song
    success_url = '/'

    def test_func(self):
        song = self.get_object()
        if self.request.user == song.contributor:
            return True
        return False 


def about(request):
    return render (request, 'songbook/about.html',{'title':about})