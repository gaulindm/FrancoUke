from django.db import migrations


def migrate_performances_to_events(apps, schema_editor):
    Performance = apps.get_model("board", "Performance")
    Event = apps.get_model("board", "Event")
    PerformanceAvailability = apps.get_model("board", "PerformanceAvailability")
    EventAvailability = apps.get_model("board", "EventAvailability")

    db_alias = schema_editor.connection.alias

    for perf in Performance.objects.using(db_alias).all():
        # Map event_type
        if perf.is_rehearsal:
            event_type = "rehearsal"
        else:
            event_type = "performance"

        # Build rich_description from extra fields (attire/chairs/etc.)
        extra_notes = []
        if perf.attire:
            extra_notes.append(f"Attire: {perf.attire}")
        if perf.chairs:
            extra_notes.append(f"Chairs: {perf.chairs}")
        if perf.venue:
            extra_notes.append(f"Venue: {perf.venue.name}")

        rich_description = "\n".join(extra_notes)

        # Create Event
        event = Event.objects.using(db_alias).create(
            board_item=perf.board_item,
            title=str(perf.board_item),  # use board_item’s __str__ as title
            rich_description=rich_description,
            event_type=event_type,
            status=perf.performance_type,  # "upcoming", "tbc", "past"
            event_date=perf.event_date,
            start_time=perf.start_time,
            end_time=perf.end_time,
            location=perf.location or (perf.venue.name if perf.venue else ""),
            created_at=perf.created_at,
        )

        # Copy availabilities
        availabilities = PerformanceAvailability.objects.using(db_alias).filter(performance=perf)
        for avail in availabilities:
            EventAvailability.objects.using(db_alias).create(
                event=event,
                user=avail.user,
                status=avail.status,
            )


def reverse_migration(apps, schema_editor):
    Performance = apps.get_model("board", "Performance")
    Event = apps.get_model("board", "Event")
    PerformanceAvailability = apps.get_model("board", "PerformanceAvailability")
    EventAvailability = apps.get_model("board", "EventAvailability")

    db_alias = schema_editor.connection.alias

    for event in Event.objects.using(db_alias).filter(event_type__in=["performance", "rehearsal"]):
        perf = Performance.objects.using(db_alias).create(
            board_item=event.board_item,
            event_date=event.event_date,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
            performance_type=event.status,
            is_rehearsal=(event.event_type == "rehearsal"),
        )

        availabilities = EventAvailability.objects.using(db_alias).filter(event=event)
        for avail in availabilities:
            PerformanceAvailability.objects.using(db_alias).create(
                performance=perf,
                user=avail.user,
                status=avail.status,
            )


class Migration(migrations.Migration):

    dependencies = [
        ("board", "0006_remove_event_description"),  # update to your actual last migration
    ]

    operations = [
        migrations.RunPython(migrate_performances_to_events, reverse_migration),
    ]
