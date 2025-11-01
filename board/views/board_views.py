# board/views/board_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.db.models import Prefetch

from ..models import BoardColumn, BoardItem, Event, EventAvailability

User = get_user_model()

# board/views/dashboard_views.py (or wherever full_board_view is defined)
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from board.models import BoardColumn
from board.utils.availability import attach_user_availability


@login_required
def full_board_view(request):
    """
    Dashboard view that renders all columns and their events/items.
    """
    today = timezone.localdate()

    columns = (
        BoardColumn.objects
        .select_related("venue")
        .prefetch_related(
            "items__photos",
            "events__photos",
            "events__availabilities",
            "venue__events__photos",
            "venue__events__availabilities",
            "messages",
        )
        .order_by("position")
    )

    for column in columns:
        if column.venue:
            events = column.venue.events.all()
        else:
            events = column.events.all()

        upcoming = events.filter(event_date__gte=today).order_by("event_date", "start_time")
        past = events.filter(event_date__lt=today).order_by("-event_date", "-start_time")

        if column.name.lower().startswith("upcoming"):
            column.sorted_events = list(upcoming)
        elif column.name.lower().startswith("past"):
            column.sorted_events = list(past)
        elif column.name.lower().startswith("to be confirmed"):
            column.sorted_events = list(events.order_by("event_date", "start_time"))
        else:
            column.sorted_events = list(upcoming) + list(past)

        # ✅ Attach current user's availability to each event
        attach_user_availability(column.sorted_events, request.user)

    return render(request, "board/full_board.html", {"columns": columns})

@login_required
def performer_event_list(request):
    """
    List of upcoming events for performers. Preloads the user's availability.
    """
    events = (
        Event.objects.filter(event_date__gte=now().date())
        .select_related("venue")
        .order_by("event_date", "start_time")
    )

    user_availability = {}
    if request.user.is_authenticated:
        availabilities = EventAvailability.objects.filter(
            user=request.user, event__in=events
        )
        user_availability = {av.event_id: av.status for av in availabilities}

    return render(request, "board/performer_event_list.html", {
        "events": events,
        "user_availability": user_availability,
    })


@login_required
def availability_matrix(request):
    """
    Matrix of performer availabilities for upcoming events.
    """
    today = timezone.localdate()

    events = Event.objects.select_related("venue").filter(
        event_date__gte=today
    ).order_by("event_date", "start_time")

    players = User.objects.filter(groups__name="Performers").order_by("username")

    matrix = []
    for player in players:
        row = []
        for event in events:
            availability = EventAvailability.objects.filter(event=event, user=player).first()
            if availability:
                if availability.status == "yes":
                    row.append("✅")
                elif availability.status == "maybe":
                    row.append("🤔")
                elif availability.status == "no":
                    row.append("❌")
                else:
                    row.append("–")
            else:
                row.append("–")
        matrix.append((player, row))

    summary = []
    for event in events:
        yes_count = EventAvailability.objects.filter(event=event, status="yes").count()
        maybe_count = EventAvailability.objects.filter(event=event, status="maybe").count()
        no_count = EventAvailability.objects.filter(event=event, status="no").count()
        summary.append(f"✅ {yes_count} / 🤔 {maybe_count} / ❌ {no_count}")

    return render(request, "board/availability_matrix.html", {
        "events": events,
        "matrix": matrix,
        "summary": summary,
    })


@login_required
def board_item_gallery_view(request, item_id):
    board_item = get_object_or_404(BoardItem, id=item_id)
    return render(request, 'board/item_gallery.html', {'board_item': board_item})


@require_GET
def item_photo_list(request, item_id):
    try:
        item = BoardItem.objects.get(id=item_id)
    except BoardItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)

    photos = item.photos.all()
    data = [{
        'url': photo.image.url,
        'caption': getattr(photo, 'caption', f"Photo {i+1}")
    } for i, photo in enumerate(photos)]

    return JsonResponse(data, safe=False)
