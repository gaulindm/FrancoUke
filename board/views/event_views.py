# board/views/event_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied

from ..models import Event, EventAvailability, BoardItem
from setlists.models import SetList  # safe import: setlists is separate app in your project
from core.group_access import group_member_required


@group_member_required
def event_detail(request, group_slug, event_id):
    """
    Event detail used by the modal include and standalone page.
    """
    group = request.group
    event = get_object_or_404(Event, id=event_id, group=group)

    # linked setlist if exists
    setlist = getattr(event, "setlist", None)

    user_status = None
    if request.user.is_authenticated:
        user_status = (
            EventAvailability.objects
            .filter(user=request.user, event=event)
            .values_list("status", flat=True)
            .first()
        )

    return render(request, "board/_event_detail.html", {
        "event": event,
        "setlist": setlist,
        "user_status": user_status,
        "group": group,
    })


@require_POST
@group_member_required
def update_event_availability(request, group_slug, event_id):
    """
    Update current user's availability for an event.
    Returns JSON for AJAX; otherwise redirects to board.
    """
    group = request.group
    status = request.POST.get("status")
    event = get_object_or_404(Event, id=event_id, group=group)

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

    return redirect("board:full_board", group_slug=group_slug)


@require_POST
@group_member_required
def set_availability(request, group_slug, event_id):
    """
    Backwards-compatible wrapper used elsewhere in the app (keeps old route).
    """
    return update_event_availability(request, group_slug, event_id)


@group_member_required
def rehearsal_detail_view(request, group_slug, pk):
    group = request.group
    event = get_object_or_404(Event, pk=pk, event_type="rehearsal", group=group)

    user_availability = None
    if request.user.is_authenticated:
        user_availability = event.availabilities.filter(user=request.user).first()

    return render(request, "board/rehearsal_detail.html", {
        "event": event,                     # ✅ add this
        "rehearsal": event,
        "user_availability": user_availability,
        "group": group,
    })