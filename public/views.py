#public/views.py
from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import render
from board.models import BoardColumn   # 👈 this line pulls the model from board


def about(request):
    return render(request, "public/about.html")

from django.shortcuts import render
from django.utils import timezone
from board.models import BoardColumn

def public_board(request):
    """
    Public board view
    - Accessible without login
    - Only shows columns/items marked as public
    - Shows all events (events don't have is_public)
    """

    today = timezone.localdate()

    # ✅ Only fetch public columns
    columns = (
        BoardColumn.objects
        .filter(is_public=True)
        .select_related("venue")
        .prefetch_related(
            "items__photos",
            "events__photos",
        )
        .order_by("position")
    )

    for column in columns:
        # 🔹 Only public items
        column.public_items = column.items.filter(is_public=True)

        # 🔹 Venue events vs column events
        if column.venue:
            events = column.venue.events.all()  # no is_public field
        else:
            events = column.events.all()

        # 🔹 Split into upcoming vs past
        upcoming = events.filter(event_date__gte=today).order_by("event_date", "start_time")
        past = events.filter(event_date__lt=today).order_by("-event_date", "-start_time")

        # 🔹 Combine
        column.sorted_events = list(upcoming) + list(past)

        # 🔹 Attach cover photo (no is_public filter on photos)
        for event in column.sorted_events:
            event._cover_photo = (
                event.photos.filter(is_cover=True).first()
                or event.photos.first()
            )

        # 🔹 Debug log
        print(
            f"Column: {column.name} ({column.column_type}) | "
            f"Events: {len(column.sorted_events)} | "
            f"Public Items: {column.public_items.count()}"
        )

    return render(request, "public/public_board.html", {"columns": columns})


def contact(request):
    return render(request, "public/contact.html")
