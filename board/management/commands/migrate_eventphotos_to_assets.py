# board/management/commands/migrate_eventphotos_to_assets.py
from django.core.management.base import BaseCommand
from django.db import transaction
from board.models import Event, EventPhoto
from assets.models import Asset
import os


class Command(BaseCommand):
    help = 'Migrate legacy EventPhotos to the Asset system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without making changes',
        )
        parser.add_argument(
            '--delete-old',
            action='store_true',
            help='Delete EventPhoto records after successful migration',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        delete_old = options['delete_old']

        if dry_run:
            self.stdout.write(self.style.WARNING('=== DRY RUN MODE - No changes will be made ===\n'))

        event_photos = EventPhoto.objects.select_related('event').all()
        total_count = event_photos.count()

        self.stdout.write(f'Found {total_count} EventPhotos to migrate\n')

        migrated_count = 0
        skipped_count = 0
        error_count = 0

        for event_photo in event_photos:
            event = event_photo.event
            
            try:
                # Check if this photo has already been migrated
                # (by checking if an Asset with the same file path exists)
                existing_asset = Asset.objects.filter(
                    file=event_photo.image.name
                ).first()

                if existing_asset:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Skipping: {event.title} - Asset already exists'
                        )
                    )
                    # Link it to the event if not already linked
                    if not dry_run and existing_asset not in event.gallery_assets.all():
                        event.gallery_assets.add(existing_asset)
                        if event_photo.is_cover:
                            event.cover_asset = existing_asset
                            event.save()
                    skipped_count += 1
                    continue

                if not dry_run:
                    with transaction.atomic():
                        # Create new Asset from EventPhoto
                        asset = Asset.objects.create(
                            type=Asset.TYPE_IMAGE,
                            provider=Asset.PROVIDER_LOCAL,
                            file=event_photo.image.name,  # Reuse existing file
                            title=f"{event.title} - Photo",
                            is_public=event.is_public,
                        )
                        
                        # Metadata/thumbnail will auto-generate via save()
                        
                        # Link to event via gallery_assets
                        event.gallery_assets.add(asset)
                        
                        # Set as cover if it was marked as cover
                        if event_photo.is_cover:
                            event.cover_asset = asset
                            event.save()

                        migrated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Migrated: {event.title} - {os.path.basename(event_photo.image.name)}'
                            )
                        )
                        
                        # Delete old EventPhoto if requested
                        if delete_old:
                            # Don't delete the actual file, just the record
                            event_photo.delete()

                else:
                    self.stdout.write(
                        f'Would migrate: {event.title} - {os.path.basename(event_photo.image.name)}'
                    )
                    if event_photo.is_cover:
                        self.stdout.write('  → Would set as cover photo')
                    migrated_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error migrating {event.title}: {str(e)}'
                    )
                )

        # Summary
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN COMPLETE - No changes made'))
        else:
            self.stdout.write(self.style.SUCCESS('MIGRATION COMPLETE'))
        
        self.stdout.write(f'Total processed: {total_count}')
        self.stdout.write(self.style.SUCCESS(f'Migrated: {migrated_count}'))
        self.stdout.write(self.style.WARNING(f'Skipped (already exists): {skipped_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        
        if not dry_run and not delete_old:
            self.stdout.write(
                self.style.WARNING(
                    '\nNote: Old EventPhoto records still exist. '
                    'Run with --delete-old to remove them after verifying migration.'
                )
            )