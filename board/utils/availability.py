from board.models import EventAvailability

def attach_user_availability(events, user):
    """
    Annotate each event with the current user's availability status.
    Adds `event.my_availability` attribute dynamically.
    """
    if not user.is_authenticated:
        for event in events:
            event.my_availability = None
        return events

    user_availabilities = {
        a.event_id: a.status
        for a in EventAvailability.objects.filter(user=user, event__in=events)
    }

    for event in events:
        event.my_availability = user_availabilities.get(event.id, None)

    return events
