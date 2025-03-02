# models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
import re
import json
from .parsers import parse_song_data  # Import the parse_song_data function
from .utils.transposer import detect_key
from taggit.managers import TaggableManager


class Song(models.Model):
    songTitle = models.CharField(max_length=100, blank=True, null=True)
    songChordPro = models.TextField()  # Original
    lyrics_with_chords = models.JSONField(null=True, blank=True)
    tags = TaggableManager(blank=True) 
    metadata = models.JSONField(blank=True, null=True)  # Stores metadata as JSON
    date_posted = models.DateField(default=timezone.now)
    contributor = models.ForeignKey(User, on_delete=models.CASCADE)
    acknowledgement = models.CharField(max_length=100, blank=True, null=True)
    #abc_notation = models.TextField(blank=True, null=True, help_text="Optional ABC notation for this song.")
    
    
    def save(self, *args, **kwargs):
        # Only parse title if songTitle is not manually set
        if not self.songTitle:
            self.songTitle, self.metadata = self.parse_metadata_from_chordpro()
        else:
            # Only update metadata
            _, self.metadata = self.parse_metadata_from_chordpro()
        
        # Parse the songChordPro content of the song
        self.lyrics_with_chords = parse_song_data(self.songChordPro)

        # Detect the key if not already specified
        if not self.metadata.get('key'):
            self.metadata['key'] = detect_key(self.lyrics_with_chords)
            
        super().save(*args, **kwargs)

    def parse_metadata_from_chordpro(self):
        # Regular expressions to find all relevant metadata tags
        tags = {
            "title": re.search(r'{(?:title|t):\s*([^\}]+)}', self.songChordPro, re.IGNORECASE | re.UNICODE),
            "comment": re.search(r'{(?:comment|c):\s*(.+?)}', self.songChordPro, re.IGNORECASE | re.UNICODE),
            "artist": re.search(r'{artist:\s*([^\}]+)}', self.songChordPro, re.IGNORECASE | re.UNICODE),
            "songwriter": re.search(r'{songwriter:\s*([^\}]+)}', self.songChordPro, re.IGNORECASE | re.UNICODE),
            "capo": re.search(r'{capo:\s*([^\}]+)}', self.songChordPro, re.IGNORECASE | re.UNICODE),
            "album": re.search(r'{album:\s*(.+?)}', self.songChordPro, re.IGNORECASE | re.UNICODE),
            "year": re.search(r'{year:\s*(\d{4})}', self.songChordPro, re.IGNORECASE),
            "key": re.search(r'{key:\s*(.+?)}', self.songChordPro, re.IGNORECASE),
            "1stnote": re.search(r'{1stnote:\s*(.+?)}', self.songChordPro, re.IGNORECASE),
            "tempo": re.search(r'{tempo:\s*(.+?)}', self.songChordPro, re.IGNORECASE),
            "timeSignature": re.search(r'{timeSignature:\s*(.+?)}', self.songChordPro, re.IGNORECASE),           
            "youtube": re.search(r'{youtube:\s*(https?://[^\s\}]+)}', self.songChordPro, re.IGNORECASE),  # New tag
        }
        
        # Extract each tag's value, or use None if not found
        metadata = {tag: match.group(1) if match else None for tag, match in tags.items()}
        
        # Set title separately as it is also stored in songTitle
        title = metadata.pop("title", "Untitled Song")

        return title, metadata      

    def __str__(self):
        return self.songTitle or "Untitled Song"
    
    def get_absolute_url(self):
        return reverse('score', kwargs={'pk': self.pk})
    
    def get_used_chords(self):
            """
            Extract chord names from the song's lyrics, handling nested lists or other complex structures.
            """
            def flatten_lyrics(lyrics):
                """
                Flatten a nested list of lyrics into a single list of strings.
                """
                flat_list = []
                for item in lyrics:
                    if isinstance(item, list):
                        flat_list.extend(flatten_lyrics(item))  # Recursively flatten nested lists
                    elif isinstance(item, str):
                        flat_list.append(item)  # Keep strings as-is
                return flat_list

            # Ensure lyrics_with_chords is flattened into a single string
            if isinstance(self.lyrics_with_chords, list):
                flat_lyrics = flatten_lyrics(self.lyrics_with_chords)
                lyrics_text = '\n'.join(flat_lyrics)  # Combine flat list into a single string
            else:
                lyrics_text = str(self.lyrics_with_chords)  # Fallback if not a list

            # Extract chord names using regex
            return list(set(re.findall(r'\[([A-G][#b]?(maj|min|dim|aug|sus|6|7|9)?)\]', lyrics_text)))
    
class SongFormatting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Each user gets their own formatting
    song = models.ForeignKey('Song', on_delete=models.CASCADE)  # Link to the song

    # Store formatting settings for each section as JSON
    intro = models.JSONField(default=dict, blank=True)
    verse = models.JSONField(default=dict, blank=True)
    chorus = models.JSONField(default=dict, blank=True)
    bridge = models.JSONField(default=dict, blank=True)
    interlude = models.JSONField(default=dict, blank=True)
    outro = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('user', 'song')  # Ensure each user has only one formatting per song

    def __str__(self):
        return f"Formatting for {self.song.songTitle} by {self.user.username}"
