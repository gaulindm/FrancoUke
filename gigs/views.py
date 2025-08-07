from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Gig, Availability
from .models import Venue
from collections import defaultdict
from django.db.models import Prefetch
from django.http import HttpResponse
from django.utils.timezone import localtime, now



User = get_user_model()

def is_leader(user):
    return user.groups.filter(name='Leaders').exists()

def is_performer(user):
    return user.groups.filter(name='Performers').exists()

def gig_home(request):
    return render(request, "gigs/home.html")


def gig_list(request):
    venues = Venue.objects.prefetch_related('gigs').all()
    return render(request, 'gigs/gig_list.html', {'venues': venues})

def add_to_calendar(request, gig_id):
    gig = get_object_or_404(Gig, pk=gig_id)
    gig_time = localtime(gig.date)  # Convert to local timezone

    # Create ICS content
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//FrancoUke//Gigs//EN
BEGIN:VEVENT
UID:{gig.id}@francouke
DTSTAMP:{gig_time.strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{gig_time.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{gig_time.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:{gig.title}
LOCATION:{gig.venue}
END:VEVENT
END:VCALENDAR
"""

    response = HttpResponse(ics_content, content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="{gig.title}.ics"'
    return response

def gig_roster(request, pk):
    gig = get_object_or_404(Gig, pk=pk)
    availabilities = gig.availability_set.select_related('player')
    return render(request, 'gigs/gig_roster.html', {
        'gig': gig,
        'availabilities': availabilities
    })






User = get_user_model()  # ✅ Use your CustomUser

@login_required
def availability_matrix(request):
    players = (
        User.objects
        .filter(groups__name='Performers', is_active=True)
        .order_by('first_name', 'last_name', 'username')
    )

    gigs = Gig.objects.order_by('date', 'start_time')

    # Lookup: {(player_id, gig_id): status_char}
    availability_dict = {
        (a.player_id, a.gig_id): a.status
        for a in Availability.objects.filter(gig__in=gigs)
    }

    STATUS_ICONS = {
        'Y': '✅',  # Yes
        'N': '❌',  # No
        'M': '🤔',  # Maybe
    }

    # Build matrix rows: (player, [status_for_each_gig])
    matrix = []
    for player in players:
        row = []
        for gig in gigs:
            status = availability_dict.get((player.id, gig.id))
            row.append(STATUS_ICONS.get(status, '—'))
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



def performer_gig_list(request):
    gigs = Gig.objects.filter(date__gte=now().date()).order_by('date', 'start_time')
    user_availability = {}

    if request.user.is_authenticated:
        # Preload the user's availability for these gigs
        availabilities = Availability.objects.filter(player=request.user, gig__in=gigs)
        user_availability = {av.gig_id: av.status for av in availabilities}

    return render(request, 'gigs/performer_gig_list.html', {
        'gigs': gigs,
        'user_availability': user_availability
    })


@login_required
def performer_gig_detail(request, gig_id):
    gig = get_object_or_404(Gig, pk=gig_id)
    availability, created = Availability.objects.get_or_create(gig=gig, player=request.user)

    if request.method == "POST":
        new_status = request.POST.get('status')
        if new_status in dict(Availability.AVAILABILITY_CHOICES):
            availability.status = new_status
            availability.save()
            return redirect('gigs:performer_gig_detail', gig_id=gig.id)

    all_availabilities = Availability.objects.filter(gig=gig).select_related('player')

    return render(request, 'gigs/performer_gig_detail.html', {
        'gig': gig,
        'availability': availability,
        'all_availabilities': all_availabilities
    })



@login_required
def performer_gig_grid(request):
    gigs = (
        Gig.objects
        .select_related('venue')
        .order_by('venue__name', 'date', 'start_time')
    )

    # Group gigs by venue
    gigs_by_venue = defaultdict(list)
    for gig in gigs:
        gigs_by_venue[gig.venue].append(gig)

    # My availability lookup
    my_availability = {
        av.gig_id: av.status
        for av in Availability.objects.filter(player=request.user, gig__in=gigs)
    }

    return render(request, 'gigs/performer_gig_grid.html', {
        'gigs_by_venue': dict(gigs_by_venue),
        'my_availability': my_availability,
    })



@login_required
def performer_gig_grid_detail(request, gig_id):
    gig = get_object_or_404(Gig, pk=gig_id)
    venue = gig.venue

    # Ensure my availability exists
    availability, created = Availability.objects.get_or_create(
        gig=gig, 
        player=request.user
    )

    # Handle my availability update
    if request.method == "POST":
        new_status = request.POST.get('status')
        if new_status in dict(Availability.AVAILABILITY_CHOICES):
            availability.status = new_status
            availability.save()
            return redirect('gigs:performer_gig_grid_detail', gig_id=gig.id)

    # All performers for this gig
    all_availabilities = Availability.objects.filter(gig=gig).select_related('player')

    # Optional: All gigs for this venue to show context
    venue_gigs = (
        Gig.objects
        .filter(venue=venue)
        .order_by('date', 'start_time')
    )

    return render(request, 'gigs/performer_gig_grid_detail.html', {
        'gig': gig,
        'venue': venue,
        'availability': availability,
        'all_availabilities': all_availabilities,
        'venue_gigs': venue_gigs,  # extra context for sidebar or navigation
    })
