from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import BoardColumn, BoardItem, Venue, EventAvailability
from django.views.decorators.http import require_GET, require_POST
# views.py
from rest_framework import viewsets
from .models import BoardItem, Event
from .serializers import BoardItemSerializer, EventSerializer
#from .serializers import PerformanceSerializer

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from django.utils.timezone import now

from django.db.models import Prefetch

from .models import BoardColumn
from django.http import HttpResponse
from django.contrib.auth import get_user_model

from django.shortcuts import render
from .models import BoardColumn

def public_board(request):
    """
    Public board view
    - Accessible without login
    - Only shows columns/events/items/photos marked as public
    """

    # ✅ Only fetch public columns
    columns = (
        BoardColumn.objects
        .filter(is_public=True)  # only public columns
        .select_related("venue")
        .prefetch_related(
            "items__photos",
            "events__photos",
            # Don't prefetch availabilities — not relevant for public
        )
        .order_by("position")
    )

    # ✅ Attach only public items/events/photos
    for column in columns:
        # public items
        column.public_items = column.items.filter(is_public=True)

        # venue events
        if column.venue:
            column.public_events = column.venue.events.filter(is_public=True)
            for event in column.public_events:
                event._cover_photo = (
                    event.photos.filter(is_public=True, is_cover=True).first()
                    or event.photos.filter(is_public=True).first()
                )
        else:
            # non-venue column events
            column.public_events = column.events.filter(is_public=True)
            for event in column.public_events:
                event._cover_photo = (
                    event.photos.filter(is_public=True, is_cover=True).first()
                    or event.photos.filter(is_public=True).first()
                )

    return render(request, "board/public_board.html", {
        "columns": columns,
    })

from django.utils import timezone

@login_required
def full_board_view(request):
    user = request.user
    today = timezone.localdate()  # gives you just the date

    columns = (
        BoardColumn.objects
        .select_related("venue")
        .prefetch_related(
            "items__photos",
            "events__photos",
            "events__availabilities",
            "venue__events__photos",
            "venue__events__availabilities",
        )
        .order_by("position")
    )

    for column in columns:
        if column.venue:
            events = column.venue.events.all()
        else:
            events = column.events.all()

        # 🔹 Split by event_date instead of 'start'
        upcoming = events.filter(event_date__gte=today).order_by("event_date", "start_time")
        past = events.filter(event_date__lt=today).order_by("-event_date", "-start_time")

        column.sorted_events = list(upcoming) + list(past)

        for event in column.sorted_events:
            availability = event.availabilities.filter(user=user).first()
            event.my_availability = availability.status if availability else None

            avails = event.availabilities.all()
            event.avail_summary = {
                "yes": avails.filter(status="yes").count(),
                "no": avails.filter(status="no").count(),
                "maybe": avails.filter(status="maybe").count(),
            }

            event._cover_photo = (
                event.photos.filter(is_cover=True).first() or event.photos.first()
            )

    return render(request, "board/full_board.html", {"columns": columns})


@require_POST
@login_required
def set_availability(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        status = request.POST.get("status")
        availability, created = EventAvailability.objects.update_or_create(
            user=request.user,
            event=event,
            defaults={"status": status},
        )
    return redirect(request.META.get("HTTP_REFERER", "performer_event_list"))







def rehearsal_detail_view(request, pk):
    rehearsal = get_object_or_404(BoardItem, pk=pk, is_rehearsal=True)

    user_availability = None
    if request.user.is_authenticated:
        user_availability = rehearsal.availabilities.filter(user=request.user).first()

    return render(request, 'board/rehearsal_detail.html', {
        'rehearsal': rehearsal,
        'user_availability': user_availability,
    })



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

    # ✅ Debug output in server log
    print(f"DEBUG: Photos for item {item_id}: {data}")

    return JsonResponse(data, safe=False)



User = get_user_model()

# views.py
@login_required
def availability_matrix(request):
    events = Event.objects.select_related("venue").order_by("event_date", "start_time")

    players = User.objects.all().order_by("username")
    matrix = []

    for player in players:
        row = []
        for event in events:
            availability = EventAvailability.objects.filter(
                event=event, user=player
            ).first()
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

    # ✅ build summary row
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
def performer_event_list(request):
    events = (
        Event.objects.filter(event_date__gte=now().date())
        .select_related("venue")  # keep if you need board columns
        .order_by("event_date", "start_time")
    )

    # preload user's availability
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



def event_detail_partial(request, event_id):
    """
    Returns the modal content for an Event (used in AJAX).
    """
    event = get_object_or_404(Event, id=event_id)
    return render(request, "partials/_event_card.html", {"event": event})

# board/views.py


# --- New: Event Detail ---
def event_detail(request, event_id):
    """
    Renders the modal body for an event.
    """
    event = get_object_or_404(Event, id=event_id)

    # Look up this user's availability if logged in
    user_status = None
    if request.user.is_authenticated:
        user_status = (
            EventAvailability.objects
            .filter(user=request.user, event=event)
            .values_list("status", flat=True)
            .first()
        )

    return render(request, "partials/_event_detail.html", {
        "event": event,
        "user_status": user_status,
    })


# --- New: Update Event Availability ---
@login_required
def update_event_availability(request, event_id):
    """
    Updates the current user's availability for a given event.
    """
    if request.method == "POST":
        status = request.POST.get("status")
        event = get_object_or_404(Event, id=event_id)

        EventAvailability.objects.update_or_create(
            user=request.user,
            event=event,
            defaults={"status": status}
        )

        # If AJAX → respond with JSON
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "status": status,
                "user": request.user.username
            })

    return redirect("full_board")




class BoardItemViewSet(viewsets.ModelViewSet):
    queryset = BoardItem.objects.all().order_by("-created_at")
    serializer_class = BoardItemSerializer

"""
class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all().order_by("-created_at")
    serializer_class = PerformanceSerializer
"""

class EventViewSet(viewsets.ModelViewSet):
    queryset = (
        Event.objects
        .select_related("board_item")
        .prefetch_related("photos")
        .order_by("event_date", "start_time", "title")
    )
    serializer_class = EventSerializer

