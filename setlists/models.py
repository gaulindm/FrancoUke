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
    setlist = models.ForeignKey("SetList", related_name="songs", on_delete=models.CASCADE)
    song = models.ForeignKey("songbook.Song", on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    rehearsal_notes = models.TextField(blank=True)

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
