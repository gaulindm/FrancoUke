from django.shortcuts import render, redirect, get_object_or_404
from .models import Gig
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Gig, Availability

User = get_user_model()

def is_leader(user):
    return user.groups.filter(name='Leaders').exists()

def is_performer(user):
    return user.groups.filter(name='Performers').exists()


def gig_roster(request, pk):
    gig = get_object_or_404(Gig, pk=pk)
    availabilities = gig.availability_set.select_related('player')
    return render(request, 'gigs/gig_roster.html', {
        'gig': gig,
        'availabilities': availabilities
    })





@login_required
@user_passes_test(is_leader)

def availability_matrix(request):
    players = (
        User.objects
        .filter(groups__name='Performers', is_active=True)
        .order_by('first_name', 'last_name', 'username')
    )

    gigs = Gig.objects.order_by('start_time')
    # Lookup: {(player_id, gig_id): status_char}
    availability_dict = {
        (a.player_id, a.gig_id): a.status
        for a in Availability.objects.all()
    }

    # Map statuses to emojis or labels
    STATUS_ICONS = {
        'Y': '✅',  # Yes
        'N': '❌',  # No
        'M': '🤔',  # Maybe
    }

    matrix = []
    for player in players:
        row = []
        for gig in gigs:
            status = availability_dict.get((player.id, gig.id))
            row.append(STATUS_ICONS.get(status, '—'))  # default —
        matrix.append((player, row))

    return render(request, 'gigs/availability_matrix.html', {
        'players': players,
        'gigs': gigs,
        'matrix': matrix,
    })



@login_required
@user_passes_test(is_performer)
def my_availability(request):
    player = request.user
    gigs = Gig.objects.order_by('start_time')

    if request.method == "POST":
        for gig in gigs:
            status = request.POST.get(f'gig_{gig.id}')
            if status:
                availability, created = Availability.objects.get_or_create(
                    gig=gig, player=player,
                    defaults={'status': status}
                )
                if not created:
                    availability.status = status
                    availability.save()
        return redirect('gigs:my_availability')

    availability_dict = {
        a.gig_id: a.status
        for a in Availability.objects.filter(player=player)
    }

    return render(request, 'gigs/my_availability.html', {
        'gigs': gigs,
        'availability_dict': availability_dict
    })

