#public/views.py
from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import render
from board.models import BoardColumn   # 👈 this line pulls the model from board


def about(request):
    return render(request, "public/about.html")

def public_board(request):
    """
    Public board view
    - Accessible without login
    - Only shows columns/events/items/photos marked as public
    """

    today = timezone.localdate()

    # ✅ Only fetch public columns
    columns = (
        BoardColumn.objects
        .filter(is_public=True)  # only public columns
        .select_related("venue")
        .prefetch_related(
            "items__photos",
            "events__photos",
        )
        .order_by("position")
    )

    for column in columns:
        # 🔹 public items
        column.public_items = column.items.filter(is_public=True)

        # 🔹 choose venue vs column events
        if column.venue:
            events = column.venue.events.filter(is_public=True)
        else:
            events = column.events.filter(is_public=True)

        # 🔹 split into upcoming vs past
        upcoming = events.filter(event_date__gte=today).order_by("event_date", "start_time")
        past = events.filter(event_date__lt=today).order_by("-event_date", "-start_time")

        # 🔹 unified sorted list
        column.public_events = list(upcoming) + list(past)

        # 🔹 attach cover photo (only public photos)
        for event in column.public_events:
            event._cover_photo = (
                event.photos.filter(is_public=True, is_cover=True).first()
                or event.photos.filter(is_public=True).first()
            )

    return render(request, "public/public_board.html", {
        "columns": columns,
    })


def contact(request):
    return render(request, "public/contact.html")
