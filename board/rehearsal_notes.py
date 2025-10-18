# board/rehearsal_notes.py

from django.db import models
from django.conf import settings
from tinymce.models import HTMLField


# ✅ Import related models lazily via string references
# Avoid direct imports to prevent circular dependency
# from .models import Event ❌   # DO NOT import directly

# Optional: If songs live in `songbook` app
#from songbook.models import Song  # Adjust path if needed

from django.db import models
from django.conf import settings
from tinymce.models import HTMLField


class RehearsalDetails(models.Model):
    """
    One-to-one model with Event, used for detailed rehearsal notes.
    """
    event = models.OneToOneField(
        "board.Event",
        on_delete=models.CASCADE,
        related_name="rehearsal_details"
    )
    notes = HTMLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rehearsal Detail"
        verbose_name_plural = "Rehearsal Details"

    def __str__(self):
        return f"Rehearsal Details for {self.event.title if self.event else 'Unknown Event'}"


class SongRehearsalNote(models.Model):
    """
    Individual song notes linked to a rehearsal.
    """
    rehearsal = models.ForeignKey(
        RehearsalDetails,
        on_delete=models.CASCADE,
        related_name="song_notes"
    )
    song = models.ForeignKey(
        "songbook.Song",
        on_delete=models.CASCADE,
        related_name="rehearsal_notes"
    )
    notes = HTMLField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["song__songTitle", "created_at"]
        verbose_name = "Song Rehearsal Note"
        verbose_name_plural = "Song Rehearsal Notes"

    def __str__(self):
        event_title = self.rehearsal.event.title if self.rehearsal and self.rehearsal.event else "Unknown Event"
        song_title = self.song.songTitle if self.song else "Unknown Song"
        return f"{song_title} @ {event_title}"

'''
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


'''