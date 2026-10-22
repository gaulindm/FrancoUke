# board/views/board_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.db.models import Prefetch, Q

from ..models import BoardColumn, BoardItem, Event, EventAvailability
from core.group_access import group_member_required

User = get_user_model()

from board.utils.availability import attach_user_availability


@group_member_required
def full_board_view(request, group_slug):
    """
    Dashboard view that renders all columns and their events/items
    for ONE group. Only members of that group (or superusers) can see it.
    """
    group = request.group
    today = timezone.localdate()

    columns = (
        BoardColumn.objects
        .filter(group=group)
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

    return render(request, "board/full_board.html", {"columns": columns, "group": group})

@group_member_required
def performer_event_list(request, group_slug):
    """
    List of upcoming events for performers in ONE group.
    Preloads the user's availability.
    """
    group = request.group
    events = (
        Event.objects.filter(group=group, event_date__gte=now().date())
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
        "group": group,
    })

@group_member_required
def availability_matrix(request, group_slug):
    """
    Matrix of performer availabilities for upcoming events that need
    availability, for ONE group.
    """
    group = request.group
    today = timezone.localdate()

    events = list(
        Event.objects
        .select_related("venue")
        .filter(
            group=group,
            event_date__gte=today,
            requires_availability=True,
        )
        .order_by("event_date", "start_time")
    )

    # Only members of THIS group appear in the matrix.
    players = list(
        User.objects
        .filter(group_memberships__group=group)
        .order_by("username")
        .distinct()
    )

    # One query for all responses: {(user_id, event_id): status}
    status_by_cell = {
        (a.user_id, a.event_id): a.status
        for a in EventAvailability.objects.filter(
            event__in=events,
            user__in=players,
        )
    }

    icons = {"yes": "✅", "maybe": "🤔", "no": "❌"}

    matrix = []
    for player in players:
        row = [
            icons.get(status_by_cell.get((player.id, event.id)), "–")
            for event in events
        ]
        matrix.append((player, row))

    # Summary counts only the players shown in the matrix
    summary = []
    for event in events:
        statuses = [status_by_cell.get((p.id, event.id)) for p in players]
        summary.append(
            f"✅ {statuses.count('yes')} / "
            f"🤔 {statuses.count('maybe')} / "
            f"❌ {statuses.count('no')}"
        )

    return render(request, "board/availability_matrix.html", {
        "events": events,
        "matrix": matrix,
        "summary": summary,
        "group": group,
    })
@group_member_required
def board_item_gallery_view(request, group_slug, item_id):
    group = request.group
    board_item = get_object_or_404(
        BoardItem.objects.filter(Q(column__group=group) | Q(event__group=group)),
        id=item_id,
    )
    return render(request, 'board/item_gallery.html', {'board_item': board_item, 'group': group})


@require_GET
@group_member_required
def item_photo_list(request, group_slug, item_id):
    group = request.group
    try:
        item = BoardItem.objects.filter(
            Q(column__group=group) | Q(event__group=group)
        ).get(id=item_id)
    except BoardItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)

    photos = item.photos.all()
    data = [{
        'url': photo.image.url,
        'caption': getattr(photo, 'caption', f"Photo {i+1}")
    } for i, photo in enumerate(photos)]

    return JsonResponse(data, safe=False)