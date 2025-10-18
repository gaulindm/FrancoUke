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
from django.utils import timezone
from django.shortcuts import render
from .models import BoardColumn

# board/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import BoardColumn, Event, EventAvailability


@login_required
def full_board_view(request):
    user = request.user
    today = timezone.localdate()

    columns = (
        BoardColumn.objects
        .select_related("venue")
        .prefetch_related(
            "items__photos",                # songs, photos
            "events__photos",               # event photos
            "events__availabilities",       # availability
            "venue__events__photos",
            "venue__events__availabilities",
            "messages",                     # general column messages
        )
        .order_by("position")
    )

    for column in columns:
        #print(f"\n🟦 Column: {column.name} (type={column.column_type})")

        # 1️⃣ Select events depending on venue binding
        if column.venue:
            events = column.venue.events.all()
        else:
            events = column.events.all()

        upcoming = events.filter(event_date__gte=today).order_by("event_date", "start_time")
        past = events.filter(event_date__lt=today).order_by("-event_date", "-start_time")

        # 2️⃣ Assign events per column type or name
        if column.name.lower().startswith("upcoming"):
            column.sorted_events = list(upcoming)
        elif column.name.lower().startswith("past"):
            column.sorted_events = list(past)
        elif column.name.lower().startswith("to be confirmed"):
            column.sorted_events = list(events.order_by("event_date", "start_time"))        
        else:
            column.sorted_events = list(upcoming) + list(past)

        
        for column in columns:
            print(f"🟦 Column: {column.name}")
            for event in getattr(column, "sorted_events", []):
                print(f"   🎭 Event: {event.title} (ID={event.id})")

                if hasattr(event, "setlist"):
                    print(f"      🎵 Has setlist: {getattr(event, 'setlist', None)}")
                else:
                    print("      🚫 No setlist attribute found.")

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
    #print(f"DEBUG: Photos for item {item_id}: {data}")

    return JsonResponse(data, safe=False)


User = get_user_model()
from django.utils import timezone

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()   # <-- this will point to users.CustomUser

@login_required
def availability_matrix(request):
    today = timezone.localdate()

    # only upcoming events
    events = Event.objects.select_related("venue").filter(
        event_date__gte=today
    ).order_by("event_date", "start_time")

    # ✅ only performers
    players = User.objects.filter(groups__name="Performers").order_by("username")

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

    # summary row
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


'''
def event_detail_partial(request, event_id):
    """
    Returns the modal content for an Event (used in AJAX).
    """
    event = get_object_or_404(Event, id=event_id)
    return render(request, "partials/_event_card.html", {"event": event})
'''
# board/views.py


# --- New: Event Detail ---
# views.py
from django.shortcuts import render, get_object_or_404
from .models import Event, EventAvailability
from setlists.models import SetList

'''def event_detail(request, event_id):
    """
    Renders the modal body for an event, including related setlist (if exists).
    Includes debug prints for troubleshooting setlist linkage.
    """
    event = get_object_or_404(Event, id=event_id)
    print("🧩 [DEBUG:event_detail] Loaded Event:", event.title, f"(ID={event.id})")

    # --- Try to get the related setlist (if it exists) ---
    if hasattr(event, "setlist"):
        setlist = getattr(event, "setlist", None)
        if setlist:
            print(f"🎵 [DEBUG:event_detail] Found related Setlist: {setlist} (ID={setlist.id})")
        else:
            print("🚫 [DEBUG:event_detail] Event has a 'setlist' attribute, but it's None.")
    else:
        print("❓ [DEBUG:event_detail] Event has no 'setlist' attribute — check model relationship.")
        setlist = None

    # --- Look up this user's availability if logged in ---
    user_status = None
    if request.user.is_authenticated:
        user_status = (
            EventAvailability.objects
            .filter(user=request.user, event=event)
            .values_list("status", flat=True)
            .first()
        )
        print(f"👤 [DEBUG:event_detail] User '{request.user.username}' availability:", user_status)
    else:
        print("👤 [DEBUG:event_detail] Anonymous user — skipping availability lookup.")

    # --- Build context ---
    context = {
        "event": event,
        "setlist": setlist,
        "user_status": user_status,
    }

    print("📦 [DEBUG:event_detail] Context keys:", list(context.keys()))
    print("📦 [DEBUG:event_detail] Setlist in context:", context["setlist"])

    return render(request, "partials/_event_detail.html", context)

'''
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

    return redirect("board:full_board")




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

# board/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import BoardColumn, BoardMessage
from .forms import BoardMessageForm
from .decorators import group_required


@login_required
@group_required("Leaders")  # 👈 only Leaders can access
def create_board_message(request, column_id):
    column = get_object_or_404(BoardColumn, pk=column_id)

    if request.method == "POST":
        form = BoardMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.column = column          # 👈 set column here
            message.author = request.user    # 👈 set author here
            message.save()
            return redirect("board:full_board")
    else:
        form = BoardMessageForm()

    return render(request, "board/message_form.html", {"form": form, "column": column})
