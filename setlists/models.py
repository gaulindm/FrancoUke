from django.db import models
from django.conf import settings
from songbook.models import Song
from board.models import Event  # optional, only if you want to attach setlists to events

class SetList(models.Model):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(
        Event, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Optional: link this setlist to a Uke4ia event"
    )

    def __str__(self):
        return self.name

class SetListSong(models.Model):
    setlist = models.ForeignKey(SetList, on_delete=models.CASCADE, related_name="songs")
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    rehearsal_notes = models.TextField(blank=True)
    scroll_speed = models.PositiveIntegerField(default=40)  # override per setlist if needed

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.order}. {self.song.songTitle}"
