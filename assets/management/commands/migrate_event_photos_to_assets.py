# assets/management/commands/migrate_event_photos_to_assets.py
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction
from django.core.files.base import ContentFile

import hashlib

CHUNK = 8192

def compute_sha256(fileobj):
    h = hashlib.sha256()
    fileobj.seek(0)
    for chunk in iter(lambda: fileobj.read(CHUNK), b''):
        h.update(chunk)
    fileobj.seek(0)
    return h.hexdigest()

class Command(BaseCommand):
    help = 'Migrate EventPhoto-like model files into Asset records and map them. Usage: manage.py migrate_event_photos_to_assets app_label.ModelName'

    def add_arguments(self, parser):
        parser.add_argument('model', help='Model to migrate, in the form app_label.ModelName (e.g., events.EventPhoto)')
        parser.add_argument('--dry-run', action='store_true', help='Dont write DB changes, just report')
        parser.add_argument('--commit', action='store_true', help='Perform DB changes (default is dry-run)')

    def handle(self, *args, **options):
        model_path = options['model']
        dry_run = options['dry_run'] and not options['commit']
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN mode - no DB changes will be made.'))
        app_label, model_name = model_path.split('.')
        Model = apps.get_model(app_label, model_name)
        Asset = apps.get_model('assets', 'Asset')
        # Provide a mapping cache for speed
        existing_hashes = {h: a for h, a in Asset.objects.values_list('sha256', 'id')}
        qs = Model.objects.all()
        total = qs.count()
        self.stdout.write(f'Found {total} objects to process...')
        processed = 0
        created = 0
        reused = 0

        for obj in qs.iterator():
            processed += 1
            # Assume the file field is named 'photo', but try to discover
            file_field = None
            for f in ['photo', 'image', 'file']:
                if hasattr(obj, f):
                    file_field = getattr(obj, f)
                    break
            if not file_field:
                self.stdout.write(self.style.ERROR(f'No recognized file field on {obj}'))
                continue
            if not file_field:
                continue
            try:
                file_obj = file_field
                # open file via storage API
                f = file_obj.open('rb')
                sha = compute_sha256(f)
                f.close()
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f'Could not open file for {obj}: {exc}'))
                continue

            asset = None
            try:
                asset = Asset.objects.filter(sha256=sha).first()
            except Exception:
                asset = None

            if asset:
                reused += 1
                self.stdout.write(f'[{processed}/{total}] Reusing asset {asset.id} for {obj}')
            else:
                created += 1
                self.stdout.write(f'[{processed}/{total}] Creating asset for {obj}')
                if not dry_run:
                    # create Asset and save file into it
                    with file_obj.open('rb') as fh:
                        content = ContentFile(fh.read())
                    # create a new Asset instance
                    new_asset = Asset(type=Asset.TYPE_IMAGE if str(content).lower().startswith('b\'\\xff') else Asset.TYPE_OTHER)
                    new_asset.title = getattr(obj, 'title', '') or ''
                    new_asset.uploaded_at = getattr(obj, 'created_at', None) or timezone.now()
                    new_asset.save()  # must have pk
                    new_asset.file.save(os.path.basename(file_obj.name), content, save=False)
                    # compute metadata/thumbnails
                    new_asset.compute_metadata_and_thumbnail(save_obj=False)
                    new_asset.save()
                    asset = new_asset

            # Now map asset id to the old record: store in a new nullable FK 'asset' if exists, or create EventAsset
            if hasattr(obj, 'asset'):
                if not dry_run:
                    obj.asset_id = asset.id
                    obj.save(update_fields=['asset'])
            else:
                # Create EventAsset (assumes fields: event FK exists as 'event' on obj)
                EventAsset = apps.get_model('assets', 'EventAsset')
                if not dry_run:
                    event = getattr(obj, 'event', None)
                    if event:
                        EventAsset.objects.create(
                            event_id=event.pk,
                            asset=asset,
                            caption=getattr(obj, 'caption', '') or '',
                            order=getattr(obj, 'order', 0) or 0,
                            is_primary=getattr(obj, 'is_primary', False) or False
                        )

        self.stdout.write(self.style.SUCCESS(f'Processed {processed}. Created {created}, reused {reused}.'))
        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run - no DB changes were made. Re-run with --commit to apply.'))
