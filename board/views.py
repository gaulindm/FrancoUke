from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import BoardColumn, BoardItem, PerformanceAvailability
from gigs.models import Gig, Venue, Availability  # <-- add Availability

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json

from .models import BoardColumn, BoardItem, PerformanceAvailability
from gigs.models import Gig, Venue, Availability


# views.py
from rest_framework import viewsets
from .models import BoardItem
from .serializers import BoardItemSerializer


class BoardItemViewSet(viewsets.ModelViewSet):
    queryset = BoardItem.objects.all().order_by("-created_at")
    serializer_class = BoardItemSerializer


from rest_framework import viewsets
from .models import Performance, Event
from .serializers import PerformanceSerializer, EventSerializer

class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all().order_by("-created_at")
    serializer_class = PerformanceSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = (
        Event.objects
        .select_related("board_item")
        .prefetch_related("photos")
        .order_by("event_date", "start_time", "title")
    )
    serializer_class = EventSerializer

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import BoardColumn, Performance, PerformanceAvailability


from .models import BoardColumn, Venue, Performance

@login_required
def full_board_view(request):
    columns = BoardColumn.objects.prefetch_related(
        'items__photos',
        'items__performance__availabilities'
    ).all()

    venues = Venue.objects.prefetch_related(
        'performances__board_item__photos',
        'performances__availabilities'
    ).all()

    user = request.user

    # Attach availability and cover photos like before
    for column in columns:
        for item in column.items.all():
            if hasattr(item, "performance"):
                availability = item.performance.availabilities.filter(user=user).first()
                item.performance.my_availability = availability.status if availability else None
                avails = item.performance.availabilities.all()
                item.performance.avail_summary = {
                    "yes": avails.filter(status="yes").count(),
                    "no": avails.filter(status="no").count(),
                    "maybe": avails.filter(status="maybe").count(),
                }
            cover = item.photos.filter(is_cover=True).first() or item.photos.first()
            item.cover_photo = cover

    # Same prep for venue performances
    for venue in venues:
        for perf in venue.performances.all():
            availability = perf.availabilities.filter(user=user).first()
            perf.my_availability = availability.status if availability else None
            avails = perf.availabilities.all()
            perf.avail_summary = {
                "yes": avails.filter(status="yes").count(),
                "no": avails.filter(status="no").count(),
                "maybe": avails.filter(status="maybe").count(),
            }
            cover = perf.board_item.photos.filter(is_cover=True).first() or perf.board_item.photos.first()
            perf.board_item.cover_photo = cover

    return render(request, 'board/full_board.html', {
        'columns': columns,
        'venues': venues,
    })



from django.shortcuts import render
from .models import BoardColumn
from gigs.models import Gig  # correct import



def public_board(request):
    # 1️⃣ Get all public board columns
    columns = BoardColumn.objects.filter(is_public=True).prefetch_related('items')

    # 2️⃣ Build a dictionary of gigs grouped by venue
    gigs = Gig.objects.select_related('venue')  # no is_public filter since field doesn't exist
    gigs_by_venue = {}
    for gig in gigs:
        if gig.venue not in gigs_by_venue:
            gigs_by_venue[gig.venue] = []
        gigs_by_venue[gig.venue].append(gig)

    # 3️⃣ Pass columns and gigs_by_venue to the template
    return render(request, 'board/public_board.html', {
        "columns": columns,
        "gigs_by_venue": gigs_by_venue,
    })


@csrf_exempt
def update_card_position(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data['item_id']
            new_column_id = data['new_column_id']
            new_position = data['new_position']

            item = BoardItem.objects.get(id=item_id)
            item.column_id = new_column_id
            item.position = new_position
            item.save()

            # Optional: reassign other cards' positions in the column
            siblings = BoardItem.objects.filter(column_id=new_column_id).exclude(id=item_id).order_by('position')
            for idx, sibling in enumerate(siblings):
                if idx >= new_position:
                    sibling.position = idx + 1
                    sibling.save()

            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid method'}, status=405)

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Performance, PerformanceAvailability


from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from .models import Performance, PerformanceAvailability

@login_required
@require_POST
def set_availability(request, performance_id):
    performance = get_object_or_404(Performance, id=performance_id)
    status = request.POST.get("status")

    availability, created = PerformanceAvailability.objects.get_or_create(
        performance=performance,
        user=request.user,
        defaults={"status": status}
    )

    if not created:
        availability.status = status
        availability.save()

    return redirect("full_board")  # or back to modal if using AJAX



@login_required
def update_availability(request, performance_id=None):
    if request.method == 'POST':
        # Allow performance_id from URL OR POST data
        performance_id = performance_id or request.POST.get('performance_id')
        status = request.POST.get('status')

        performance = get_object_or_404(Performance, id=performance_id)

        PerformanceAvailability.objects.update_or_create(
            user=request.user,
            performance=performance,
            defaults={'status': status}
        )

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "status": status,
                "user": request.user.username
            })

    return redirect('full_board')


def rehearsal_detail_view(request, pk):
    rehearsal = get_object_or_404(BoardItem, pk=pk, is_rehearsal=True)

    user_availability = None
    if request.user.is_authenticated:
        user_availability = rehearsal.availabilities.filter(user=request.user).first()

    return render(request, 'board/rehearsal_detail.html', {
        'rehearsal': rehearsal,
        'user_availability': user_availability,
    })

# board/views.py
from django.shortcuts import get_object_or_404, render
from .models import BoardItem

def board_item_gallery_view(request, item_id):
    board_item = get_object_or_404(BoardItem, id=item_id)
    return render(request, 'board/item_gallery.html', {'board_item': board_item})

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import BoardItem

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

