from django.db.models import Avg, Count

from .models import SongRating

# The five faces, worst (1) to best (5). Bootstrap Icons class names.
FACE_ICONS = ["bi-emoji-dizzy", "bi-emoji-frown", "bi-emoji-neutral", "bi-emoji-smile", "bi-emoji-laughing"]


def face_icon(avg):
    """The face nearest to an average score (4.5 rounds up, like Django's floatformat)."""
    if avg is None:
        return ""
    return FACE_ICONS[min(max(int(float(avg) + 0.5), 1), 5) - 1]


def _number(value):
    # MySQL hands back Decimal for averages; plain floats are easier to sort and format
    return None if value is None else float(value)


def rating_summaries(song_ids=None):
    """Everyone's scores, grouped by song: {song_id: {"avg", "n", "avg_play", "avg_sing"}}.

    song_ids=None means "every song that has been rated" (used when sorting the
    whole list by rating). One query either way. Plain aggregates are safe here
    because SongRating is queried on its own, with no tag JOINs to duplicate rows.
    """
    rows = SongRating.objects.all()
    if song_ids is not None:
        rows = rows.filter(song_id__in=song_ids)
    rows = rows.values("song_id").annotate(
        avg=Avg("stars"),
        n=Count("stars"),  # counts only rows that have an overall score
        avg_play=Avg("playability"),
        avg_sing=Avg("singability"),
    )
    return {
        row["song_id"]: {
            "avg": _number(row["avg"]),
            "n": row["n"],
            "avg_play": _number(row["avg_play"]),
            "avg_sing": _number(row["avg_sing"]),
        }
        for row in rows
    }


def rating_data(song_ids, user):
    """For the setlist page: (everyone's summaries, {song_id: this user's own SongRating})."""
    summaries = rating_summaries(song_ids)
    mine = {}
    if user.is_authenticated:
        mine = {r.song_id: r for r in SongRating.objects.filter(user=user, song_id__in=song_ids)}
    return summaries, mine