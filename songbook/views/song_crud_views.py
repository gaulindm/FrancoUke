# songbook/views/song_crud_views.py

from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from songbook.models import Song
from songbook.context_processors import site_context
from songbook.parsers import parse_song_data


class SongCreateView(LoginRequiredMixin, CreateView):
    model = Song
    fields = [
        "songTitle",
        "songChordPro",
        "is_public",  # 🆕 Add privacy field
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
        "is_public",  # 🆕 Add privacy field
        "lyrics_with_chords",
        "metadata",
        "revised_on",
        "tags",
        "acknowledgement",
    ]

    def test_func(self):
        # 🆕 Only song owner can edit
        song = self.get_object()
        return self.request.user == song.contributor

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

    def test_func(self):
        song = self.get_object()
        return self.request.user == song.contributor
    
    def get_success_url(self):
        # Redirect to user's collection after deleting
        return reverse('songbook:user-songs', kwargs={'username': self.request.user.username})


# 🆕 NEW VIEWS FOR PRIVACY MANAGEMENT

@login_required
@require_POST
def toggle_privacy(request, song_id):
    """Toggle a song between public and private."""
    song = get_object_or_404(Song, id=song_id, contributor=request.user)
    
    song.is_public = not song.is_public
    song.save()
    
    context_data = site_context(request)
    site_name = context_data.get("site_name")
    
    if site_name == "FrancoUke":
        if song.is_public:
            messages.success(request, f'"{song.songTitle}" est maintenant publique!')
        else:
            messages.info(request, f'"{song.songTitle}" est maintenant privée.')
    else:
        if song.is_public:
            messages.success(request, f'"{song.songTitle}" is now public!')
        else:
            messages.info(request, f'"{song.songTitle}" is now private.')
    
    return redirect('songbook:user-songs', username=request.user.username)


@login_required
@require_POST
def clone_song(request, song_id):
    """Create a personal copy of a public song."""
    original = get_object_or_404(Song, id=song_id, is_public=True)
    
    context_data = site_context(request)
    site_name = context_data.get("site_name")
    
    # Determine suffix based on site
    if site_name == "FrancoUke":
        suffix = "(Ma version)"
        success_msg = f'Créé votre version personnelle de "{original.songTitle}"! Vous pouvez maintenant la modifier.'
    else:
        suffix = "(My Version)"
        success_msg = f'Created your personal version of "{original.songTitle}"! You can now edit it.'
    
    # Create a clone
    cloned = Song.objects.create(
        songTitle=f"{original.songTitle} {suffix}",
        songChordPro=original.songChordPro,
        contributor=request.user,
        is_public=False,  # Private by default
        cloned_from=original,
        site_name=original.site_name,
        lyrics_with_chords=original.lyrics_with_chords,
        metadata=original.metadata,
        scroll_speed=original.scroll_speed,
    )
    
    # Copy tags
    cloned.tags.set(original.tags.all())
    
    messages.success(request, success_msg)
    
    return redirect('songbook:song_update', pk=cloned.id)


@login_required
def make_public(request, song_id):
    """Quick action to make a song public (GET allowed for convenience)."""
    song = get_object_or_404(Song, id=song_id, contributor=request.user)
    
    if not song.is_public:
        song.is_public = True
        song.save()
        
        context_data = site_context(request)
        site_name = context_data.get("site_name")
        
        if site_name == "FrancoUke":
            messages.success(request, f'"{song.songTitle}" est maintenant publique!')
        else:
            messages.success(request, f'"{song.songTitle}" is now public!')
    
    # Redirect back to where they came from, or user songs page
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('songbook:user-songs', username=request.user.username)


@login_required
def make_private(request, song_id):
    """Quick action to make a song private (GET allowed for convenience)."""
    song = get_object_or_404(Song, id=song_id, contributor=request.user)
    
    if song.is_public:
        song.is_public = False
        song.save()
        
        context_data = site_context(request)
        site_name = context_data.get("site_name")
        
        if site_name == "FrancoUke":
            messages.info(request, f'"{song.songTitle}" est maintenant privée.')
        else:
            messages.info(request, f'"{song.songTitle}" is now private.')
    
    # Redirect back to where they came from, or user songs page
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('songbook:user-songs', username=request.user.username)