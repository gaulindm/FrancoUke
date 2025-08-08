from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import BoardColumn, BoardItem, RehearsalAvailability
from gigs.models import Gig, Venue, Availability  # <-- add Availability

def full_board_view(request):
    columns = BoardColumn.objects.prefetch_related('items').all()
    rehearsals = BoardItem.objects.filter(is_rehearsal=True).select_related('column')
    gigs_by_venue = {}

    venues = Venue.objects.all()
    for venue in venues:
        gigs = Gig.objects.filter(venue=venue, date__gte=timezone.now()).order_by('date')
        if gigs.exists():
            gigs_by_venue[venue] = gigs

    if request.user.is_authenticated:
        user = request.user

        # 🎵 Rehearsals
        for column in columns:
            for item in column.items.all():
                if item.is_rehearsal:
                    availability = RehearsalAvailability.objects.filter(user=user, rehearsal=item).first()
                    item.my_availability = availability.status if availability else None

        # 🎤 Gigs
        for venue, gigs in gigs_by_venue.items():
            for gig in gigs:
                availability = Availability.objects.filter(player=user, gig=gig).first()
                gig.my_availability = availability.status if availability else None

    return render(request, 'board/full_board.html', {
        'columns': columns,
        'gigs_by_venue': gigs_by_venue,
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


@login_required
def update_availability(request):
    if request.method == 'POST':
        rehearsal_id = request.POST.get('rehearsal_id')
        status = request.POST.get('status')

        try:
            rehearsal = BoardItem.objects.get(id=rehearsal_id, is_rehearsal=True)
        except BoardItem.DoesNotExist:
            return redirect('full_board')

        RehearsalAvailability.objects.update_or_create(
            user=request.user,
            rehearsal=rehearsal,
            defaults={'status': status}
        )

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
from .models import BoardItem

def item_photo_list(request, item_id):
    item = BoardItem.objects.get(id=item_id)
    photos = item.photos.all()
    data = [{
        'url': photo.image.url,
        'caption': f"Photo {i+1}"
    } for i, photo in enumerate(photos)]
    return JsonResponse(data, safe=False)

