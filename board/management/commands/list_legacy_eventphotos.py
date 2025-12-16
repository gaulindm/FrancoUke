# board/management/commands/list_legacy_eventphotos.py
from django.core.management.base import BaseCommand
from django.db.models import Count
from board.models import Event, EventPhoto
import csv
from pathlib import Path


class Command(BaseCommand):
    help = 'List all events still using legacy EventPhotos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            help='Export results to CSV file (e.g., legacy_photos.csv)',
        )
        parser.add_argument(
            '--venue',
            type=str,
            help='Filter by venue name',
        )

    def handle(self, *args, **options):
        csv_file = options.get('csv')
        venue_filter = options.get('venue')

        # Get events with EventPhotos
        events_query = Event.objects.filter(
            photos__isnull=False
        ).annotate(
            photo_count=Count('photos')
        ).distinct().order_by('event_date', 'venue__name')

        # Apply venue filter if specified
        if venue_filter:
            events_query = events_query.filter(venue__name__icontains=venue_filter)

        events_with_photos = list(events_query)

        # Console output
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("EVENTS STILL USING LEGACY EventPhotos"))
        self.stdout.write("=" * 80)
        
        if venue_filter:
            self.stdout.write(f"\nFiltered by venue: {venue_filter}")
        
        self.stdout.write(f"\nTotal events with legacy photos: {len(events_with_photos)}\n")

        # Detailed list
        for event in events_with_photos:
            event_date = event.event_date.strftime("%Y-%m-%d") if event.event_date else "No date"
            venue_name = event.venue.name if event.venue else "No venue"
            
            self.stdout.write(
                self.style.HTTP_INFO(
                    f"\n📅 {event_date} | {event.title}"
                )
            )
            self.stdout.write(f"   Venue: {venue_name}")
            self.stdout.write(f"   Type: {event.get_event_type_display()}")
            self.stdout.write(f"   Status: {event.get_status_display()}")
            self.stdout.write(
                f"   Legacy Photos: {event.photo_count} | "
                f"Gallery Assets: {event.gallery_assets.count()}"
            )
            
            # Show individual photos
            for photo in event.photos.all():
                cover_mark = self.style.WARNING("⭐ COVER") if photo.is_cover else ""
                uploaded = photo.uploaded_at.strftime("%Y-%m-%d") if hasattr(photo, 'uploaded_at') else "Unknown"
                self.stdout.write(
                    f"      → {Path(photo.image.name).name} {cover_mark} (uploaded: {uploaded})"
                )

        # Summary by venue
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("SUMMARY BY VENUE:"))
        self.stdout.write("=" * 80 + "\n")

        venues = {}
        for event in events_with_photos:
            venue_name = event.venue.name if event.venue else "No Venue"
            if venue_name not in venues:
                venues[venue_name] = []
            venues[venue_name].append(event)

        for venue_name, events in sorted(venues.items()):
            total_photos = sum(e.photo_count for e in events)
            self.stdout.write(
                self.style.HTTP_INFO(
                    f"\n{venue_name}: {len(events)} events, {total_photos} photos"
                )
            )
            for event in sorted(events, key=lambda e: e.event_date or ''):
                event_date = event.event_date.strftime("%Y-%m-%d") if event.event_date else "No date"
                self.stdout.write(f"  - {event_date}: {event.title} ({event.photo_count} photos)")

        # Export to CSV if requested
        if csv_file:
            self._export_to_csv(events_with_photos, csv_file)

        # Final summary
        total_legacy_photos = sum(e.photo_count for e in events_with_photos)
        total_events_with_assets = sum(1 for e in events_with_photos if e.gallery_assets.count() > 0)
        
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("FINAL SUMMARY:"))
        self.stdout.write("=" * 80)
        self.stdout.write(f"Events with legacy photos: {len(events_with_photos)}")
        self.stdout.write(f"Total legacy photos: {total_legacy_photos}")
        self.stdout.write(f"Events also using new Asset system: {total_events_with_assets}")
        self.stdout.write(
            self.style.WARNING(
                f"Events ONLY using legacy system: {len(events_with_photos) - total_events_with_assets}"
            )
        )

    def _export_to_csv(self, events, filename):
        """Export event data to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Event Title', 'Event Date', 'Venue', 'Event Type', 'Status',
                'Legacy Photo Count', 'Asset Count', 'Cover Photo', 'Photo Files'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for event in events:
                photo_files = ", ".join([Path(p.image.name).name for p in event.photos.all()])
                cover_photos = [p for p in event.photos.all() if p.is_cover]
                cover_photo = Path(cover_photos[0].image.name).name if cover_photos else "None"

                writer.writerow({
                    'Event Title': event.title,
                    'Event Date': event.event_date.strftime("%Y-%m-%d") if event.event_date else "",
                    'Venue': event.venue.name if event.venue else "",
                    'Event Type': event.get_event_type_display(),
                    'Status': event.get_status_display(),
                    'Legacy Photo Count': event.photo_count,
                    'Asset Count': event.gallery_assets.count(),
                    'Cover Photo': cover_photo,
                    'Photo Files': photo_files
                })

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Exported to {filename}")
        )