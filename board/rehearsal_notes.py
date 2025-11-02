# board/rehearsal_notes.py

from django.db import models
from django.conf import settings
from tinymce.models import HTMLField

#from .models import Event

class RehearsalDetails(models.Model):
    """
    Extended details and notes for rehearsal-type Events.

    Linked one-to-one with an Event where event.event_type == "rehearsal".

    This model allows directors or leaders to record rich rehearsal notes,
    attach structured song comments, or segment the rehearsal into sections.
    """

    event = models.OneToOneField(
        "board.Event",
        on_delete=models.CASCADE,
        related_name="rehearsal_details"
    )

    notes = HTMLField(blank=True, null=True, help_text="General notes for this rehearsal")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rehearsal Detail"
        verbose_name_plural = "Rehearsal Details"

    def __str__(self):
        return f"Rehearsal Details for {self.event.title if self.event else 'Unknown Event'}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("board:rehearsal_detail", args=[self.event.id])


class SongRehearsalNote(models.Model):
    """
    Notes attached to specific songs rehearsed in a given RehearsalDetails session.

    Ideal for tracking progress, focus areas, or personalized performance feedback.
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

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("board:song_rehearsal_note_detail", args=[self.pk])


# 🧱 Optional Future Expansion
# class RehearsalSection(models.Model):
#     """
#     Logical section within a rehearsal, e.g.:
#     'Debrief - Empire Living Centre' or 'Songs We Worked On Tonight'.
#     """
#     rehearsal = models.ForeignKey(
#         RehearsalDetails,
#         on_delete=models.CASCADE,
#         related_name="sections"
#     )
#     title = models.CharField(max_length=200)
#     order = models.PositiveIntegerField(default=0)
#     body = HTMLField(blank=True, null=True)
#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         ordering = ["order"]
#         verbose_name = "Rehearsal Section"
#         verbose_name_plural = "Rehearsal Sections"
#
#     def __str__(self):
#         return f"{self.rehearsal.event.title} - {self.title}"

