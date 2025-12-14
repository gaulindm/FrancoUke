# assets/management/commands/generate_thumbnails.py
from django.core.management.base import BaseCommand
from assets.models import Asset


class Command(BaseCommand):
    help = 'Generate thumbnails for all assets that are missing them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate thumbnails even if they already exist',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)

        if force:
            assets = Asset.objects.filter(type=Asset.TYPE_IMAGE, file__isnull=False)
            self.stdout.write(f'Regenerating thumbnails for {assets.count()} image assets...')
        else:
            assets = Asset.objects.filter(
                type=Asset.TYPE_IMAGE,
                file__isnull=False,
                thumbnail=''
            )
            self.stdout.write(f'Generating thumbnails for {assets.count()} image assets...')

        success_count = 0
        error_count = 0

        for asset in assets:
            try:
                # Clear existing thumbnail if forcing
                if force and asset.thumbnail:
                    asset.thumbnail.delete(save=False)
                
                # Generate metadata and thumbnail
                changed = asset.compute_metadata_and_thumbnail(save_obj=True)
                
                if changed:
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Generated thumbnail for: {asset.title or asset.id}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ No changes for: {asset.title or asset.id}')
                    )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing {asset.title or asset.id}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Success: {success_count}, Errors: {error_count}'
            )
        )