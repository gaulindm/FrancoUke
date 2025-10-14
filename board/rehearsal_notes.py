# board/rehearsal_notes.py

from django.db import models
from django.conf import settings
#from ckeditor.fields import RichTextField
from tinymce.models import HTMLField


# ✅ Import related models lazily via string references
# Avoid direct imports to prevent circular dependency
# from .models import Event ❌   # DO NOT import directly

# Optional: If songs live in `songbook` app
#from songbook.models import Song  # Adjust path if needed


class RehearsalDetails(models.Model):
    """
    One-to-one model with Event, used for detailed rehearsal notes.
    This replaces the inline definition from models.py.
    """
    event = models.OneToOneField(
        "board.Event", 
        on_delete=models.CASCADE,
        related_name="rehearsal_details"
    )
    notes = HTMLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # ✅ add this

    def __str__(self):
        return f"Rehearsal Details for {self.event.title if self.event else 'Unknown Event'}"


class RehearsalSection(models.Model):
    """
    Logical section within a rehearsal, e.g.:
    'Debrief - Empire Living Centre' or 'Songs We Worked On Tonight'.
    """
    rehearsal = models.ForeignKey(
        RehearsalDetails,
        on_delete=models.CASCADE,
        related_name="sections"
    )
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    body = HTMLField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Rehearsal Section"
        verbose_name_plural = "Rehearsal Sections"

    def __str__(self):
        return f"{self.rehearsal.event.title} - {self.title}"


class SongRehearsalNote(models.Model):
    section = models.ForeignKey(RehearsalSection, on_delete=models.CASCADE, related_name="song_notes")
    song = models.ForeignKey("songbook.Song", on_delete=models.CASCADE, related_name="rehearsal_notes")
    notes = HTMLField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["song", "created_at"]  # ✅ fixed
        verbose_name = "Song Rehearsal Note"
        verbose_name_plural = "Song Rehearsal Notes"

    def __str__(self):
        return f"{self.song.songTitle} @ {self.section.rehearsal.event.title}"
