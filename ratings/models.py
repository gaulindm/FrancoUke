from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

# Every score is optional (null), but when it is given it must be 1 to 5.
_STAR_VALIDATORS = [MinValueValidator(1), MaxValueValidator(5)]


def _one_to_five(field_name):
    """CheckConstraint condition: the field is empty, or between 1 and 5."""
    return Q(**{f"{field_name}__isnull": True}) | Q(
        **{f"{field_name}__gte": 1, f"{field_name}__lte": 5}
    )


class SongRating(models.Model):
    """One member's opinion of one song: three optional 1-5 scores and a comment.

    Deliberately a separate model (and app): Song gets no new fields, so the
    whole feature can be removed without touching the song table.
    """

    song = models.ForeignKey(
        "songbook.Song", on_delete=models.CASCADE, related_name="ratings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="song_ratings"
    )

    stars = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=_STAR_VALIDATORS,
        help_text="Overall enjoyment, 1-5",
    )
    playability = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=_STAR_VALIDATORS,
        help_text="How easy it is to play, 1-5",
    )
    singability = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=_STAR_VALIDATORS,
        help_text="How good it is to sing, 1-5",
    )
    comment = models.TextField(blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["song", "user"], name="one_rating_per_user_per_song"
            ),
            models.CheckConstraint(condition=_one_to_five("stars"), name="rating_stars_1_to_5"),
            models.CheckConstraint(condition=_one_to_five("playability"), name="rating_playability_1_to_5"),
            models.CheckConstraint(condition=_one_to_five("singability"), name="rating_singability_1_to_5"),
        ]

    def __str__(self):
        return f"{self.user} rated {self.song_id}: {self.stars}"
