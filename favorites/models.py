# favorites/models.py
from django.conf import settings
from django.db import models


class SongFavorite(models.Model):
    """
    One row = one member hearted one song.

    Positive-only by design: there is no score and no comment, and un-hearting
    simply deletes the row, so nothing negative is ever recorded.

    There is deliberately no `group` column. The chord sheet is not tied to one
    club, so a club's count is worked out from who hearted the song and which
    club(s) that person belongs to (see favorites/utils.py).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="song_favorites",
    )
    song = models.ForeignKey(
        "songbook.Song",
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "song"], name="unique_favorite_per_user_song"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ♥ {self.song}"