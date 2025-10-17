# board/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.http import require_GET, require_POST

from django.contrib.auth import get_user_model

from rest_framework import viewsets

from .models import (
    BoardColumn,
    BoardItem,
    Event,
    EventAvailability,
)
from .serializers import (
    BoardItemSerializer,
    EventSerializer,
)
from .forms import BoardMessageForm
from .decorators import group_required

User = get_user_model()

# ------------------------------------------------------------
# 🟩 BOARD VIEWS
# ------------------------------------------------------------

@login_required
def full_board_view(request):
    """
    Displays all board columns, each containing related events.
    Events are sorted depending on column type (Upcoming, Past, etc.).
    """
    user = request.user
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
        # Select related events
        events = column.venue.events.all() if column.venue else column.events.all()

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

    return render(request, "board/full_board.html", {"columns": columns})


# ------------------------------------------------------------
# 🟨 AVAILABILITY MANAGEMENT
# ------------------------------------------------------------

@require_POST
@login_required
def set_availability(request, event_id):
    """
    Updates or creates availability for the logged-in user for a given event.
    """
    event = get_object_or_404(Event, id=event_id)
    status = request.POST.get("status")

    EventAvailability.objects.update_or_create(
        user=request.user,
        event=event,
        defaults={"status": status},
    )

    return redirect(request.META.get("HTTP_REFERER", "performer_event_list"))


@login_required
def update_event_availability(request, event_id):
    """
    Updates the user's event availability; supports AJAX or standard POST.
    """
    if request.method == "POST":
        status = request.POST.get("status")
        event = get_object_or_404(Event, id=event_id)

        EventAvailability.objects.update_or_create(
            user=request.user,
            event=event,
            defaults={"status": status}
        )

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "status": status,
                "user": request.user.username
            })

    return redirect("board:full_board")


@login_required
def availability_matrix(request):
    """
    Displays a matrix of performer availability across upcoming events.
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
            availability = EventAvailability.objects.filter(
                event=event, user=player
            ).first()
            if not availability:
                row.append("–")
                continue

            status_icon = {
                "yes": "✅",
                "maybe": "🤔",
                "no": "❌",
            }.get(availability.status, "–")
            row.append(status_icon)

        matrix.append((player, row))

    summary = []
    for event in events:
        yes = EventAvailability.objects.filter(event=event, status="yes").count()
        maybe = EventAvailability.objects.filter(event=event, status="maybe").count()
        no = EventAvailability.objects.filter(event=event, status="no").count()
        summary.append(f"✅ {yes} / 🤔 {maybe} / ❌ {no}")

    return render(request, "board/availability_matrix.html", {
        "events": events,
        "matrix": matrix,
        "summary": summary,
    })


# ------------------------------------------------------------
# 🟦 REHEARSAL / ITEM VIEWS
# ------------------------------------------------------------

def rehearsal_detail_view(request, pk):
    rehearsal = get_object_or_404(BoardItem, pk=pk, is_rehearsal=True)
    user_availability = (
        rehearsal.availabilities.filter(user=request.user).first()
        if request.user.is_authenticated
        else None
    )
    return render(request, "board/rehearsal_detail.html", {
        "rehearsal": rehearsal,
        "user_availability": user_availability,
    })


def board_item_gallery_view(request, item_id):
    board_item = get_object_or_404(BoardItem, id=item_id)
    return render(request, "board/item_gallery.html", {"board_item": board_item})


@require_GET
def item_photo_list(request, item_id):
    """
    Returns JSON list of photos for a board item.
    """
    try:
        item = BoardItem.objects.get(id=item_id)
    except BoardItem.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)

    photos = item.photos.all()
    data = [
        {"url": p.image.url, "caption": getattr(p, "caption", f"Photo {i+1}")}
        for i, p in enumerate(photos)
    ]
    return JsonResponse(data, safe=False)


@login_required
def performer_event_list(request):
    """
    Displays upcoming events for performers with availability info.
    """
    events = (
        Event.objects.filter(event_date__gte=now().date())
        .select_related("venue")
        .order_by("event_date", "start_time")
    )

    availabilities = EventAvailability.objects.filter(
        user=request.user, event__in=events
    )
    user_availability = {av.event_id: av.status for av in availabilities}

    return render(request, "board/performer_event_list.html", {
        "events": events,
        "user_availability": user_availability,
    })


# ------------------------------------------------------------
# 🟧 API ENDPOINTS (Django REST Framework)
# ------------------------------------------------------------

class BoardItemViewSet(viewsets.ModelViewSet):
    queryset = BoardItem.objects.all().order_by("-created_at")
    serializer_class = BoardItemSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = (
        Event.objects
        .select_related("board_item")
        .prefetch_related("photos")
        .order_by("event_date", "start_time", "title")
    )
    serializer_class = EventSerializer


# ------------------------------------------------------------
# 🟥 LEADER-ONLY MESSAGE CREATION
# ------------------------------------------------------------

@login_required
@group_required("Leaders")
def create_board_message(request, column_id):
    """
    Leaders can create board messages attached to columns.
    """
    column = get_object_or_404(BoardColumn, pk=column_id)

    if request.method == "POST":
        form = BoardMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.column = column
            message.author = request.user
            message.save()
            return redirect("board:full_board")
    else:
        form = BoardMessageForm()

    return render(request, "board/message_form.html", {
        "form": form,
        "column": column,
    })
