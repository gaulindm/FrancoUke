#setlist/models.py
from django.db import models
from django.db.models import Max
from django.conf import settings
from songbook.models import Song
from board.models import Event  # optional, only if you want to attach setlists to events

class SetList(models.Model):
    group = models.ForeignKey(
        "core.Group", on_delete=models.CASCADE, null=True, blank=True, related_name="setlists"
    )
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    event = models.OneToOneField(
    Event,
    on_delete=models.SET_NULL,
    null=True, blank=True,
    related_name="setlist",  # 👈 gives us event.setlist
    help_text="Optional: link this setlist to an event"
)

    def __str__(self):
        return self.name

class SetListSong(models.Model):
    setlist = models.ForeignKey("SetList", related_name="songs", on_delete=models.CASCADE)
    song = models.ForeignKey("songbook.Song", on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    

    class Meta:
        unique_together = ("setlist", "order")
        ordering = ["order"]

    def save(self, *args, **kwargs):
        # If no order is given, place it at the end
        if self.order is None:
            max_order = SetListSong.objects.filter(setlist=self.setlist).aggregate(
                Max("order")
            )["order__max"] or 0
            self.order = max_order + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.setlist.name} – {self.order}. {self.song.songTitle}"


class SongSuggestion(models.Model):
    """
    One row per song per club: the thing a leader reviews.
    Who suggested it lives in SongSuggester (one row per member).
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"

    group = models.ForeignKey(
        "core.Group", on_delete=models.CASCADE, related_name="song_suggestions"
    )
    song = models.ForeignKey(
        "songbook.Song", on_delete=models.CASCADE, related_name="suggestions"
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="reviewed_song_suggestions",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    leader_comment = models.CharField(max_length=300, blank=True)
    added_to_setlist = models.ForeignKey(
        "SetList",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="approved_suggestions",
        help_text="Setlist the song was added to when approved",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("group", "song")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.song.songTitle} ({self.group.name}) – {self.get_status_display()}"


class SongSuggester(models.Model):
    """One member's vote/note for a SongSuggestion."""

    suggestion = models.ForeignKey(
        SongSuggestion, on_delete=models.CASCADE, related_name="suggesters"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="song_suggestions",
    )
    note = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("suggestion", "user")
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user} suggested {self.suggestion.song.songTitle}"