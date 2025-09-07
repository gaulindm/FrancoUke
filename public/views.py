#public/views.py
from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import render
from board.models import BoardColumn   # 👈 this line pulls the model from board


def about(request):
    return render(request, "public/about.html")

from django.utils import timezone
from django.shortcuts import render
from board.models import BoardColumn

def public_board(request):
    """
    Public board view
    - No login required
    - Shows events/items/photos but ignores availabilities
    """

    today = timezone.localdate()

    columns = (
        BoardColumn.objects
        .select_related("venue")
        .prefetch_related(
            "items__photos",
            "events__photos",
            "venue__events__photos",
        )
        .order_by("position")
    )

    for column in columns:
        if column.venue:
            events = column.venue.events.all()
        else:
            events = column.events.all()

        # 🔹 Split by event_date
        upcoming = events.filter(event_date__gte=today).order_by("event_date", "start_time")
        past = events.filter(event_date__lt=today).order_by("-event_date", "-start_time")

        # 🔹 Unified sorted list
        column.sorted_events = list(upcoming) + list(past)

        # 🔹 Attach cover photo
        for event in column.sorted_events:
            event._cover_photo = (
                event.photos.filter(is_cover=True).first()
                or event.photos.first()
            )

    return render(request, "public/public_board.html", {"columns": columns})



def contact(request):
    return render(request, "public/contact.html")
