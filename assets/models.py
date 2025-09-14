# assets/models.py
import os
import uuid
import hashlib
import mimetypes
import subprocess
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.utils import timezone
from django.utils.html import mark_safe
from django.core.files.storage import default_storage
from PIL import Image

# Helper for upload path
def asset_upload_to(instance, filename):
    ext = filename.split('.')[-1] if '.' in filename else ''
    # Group by year/month to keep S3 keys/readability manageable
    now = timezone.now()
    return f'assets/{now.year}/{now.month:02d}/{instance.id}.{ext}'

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    def __str__(self):
        return self.name

class Asset(models.Model):
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_OTHER = 'other'
    TYPE_CHOICES = [
        (TYPE_IMAGE, 'Image'),
        (TYPE_VIDEO, 'Video'),
        (TYPE_OTHER, 'Other'),
    ]

    PROVIDER_LOCAL = 'local'
    PROVIDER_YOUTUBE = 'youtube'
    PROVIDER_VIMEO = 'vimeo'
    PROVIDER_OTHER = 'other'
    PROVIDER_CHOICES = [
        (PROVIDER_LOCAL, 'Local'),
        (PROVIDER_YOUTUBE, 'YouTube'),
        (PROVIDER_VIMEO, 'Vimeo'),
        (PROVIDER_OTHER, 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_IMAGE)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default=PROVIDER_LOCAL)

    # Either file (local) OR external_url (YouTube/Vimeo)
    file = models.FileField(upload_to=asset_upload_to, null=True, blank=True)
    external_url = models.URLField(null=True, blank=True)

    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # 👈 add this

    caption = models.TextField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)

    mime_type = models.CharField(max_length=100, blank=True)
    size = models.BigIntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # seconds for video

    sha256 = models.CharField(max_length=64, db_index=True, null=True, blank=True)
    is_public = models.BooleanField(default=True)

    thumbnail = models.ImageField(upload_to='assets/thumbnails/', null=True, blank=True)

    tags = models.ManyToManyField(Tag, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='uploaded_assets'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['sha256']),
            models.Index(fields=['uploaded_at']),
        ]

    def __str__(self):
        return self.title or f'Asset {self.id}'

    # -----------------------
    # Utility helpers
    # -----------------------
    def _compute_hash(self, file_obj, chunk_size=8192):
        h = hashlib.sha256()
        file_obj.seek(0)
        for chunk in iter(lambda: file_obj.read(chunk_size), b''):
            h.update(chunk)
        file_obj.seek(0)
        return h.hexdigest()

    def _guess_mime(self, filename):
        t, _ = mimetypes.guess_type(filename)
        return t or ''

    def _generate_image_thumbnail(self, pil_img, size=(400, 400)):
        pil_img.thumbnail(size, Image.LANCZOS)
        buf = BytesIO()
        pil_img.save(buf, format='JPEG', quality=85)
        buf.seek(0)
        return ContentFile(buf.read(), name=f'{self.id}_thumb.jpg')

    def _attempt_video_frame(self, source_path, time='00:00:02'):
        """
        Try to extract a single frame using ffmpeg if available.
        Returns ContentFile or None.
        """
        try:
            tmp_out = f'/tmp/{self.id}_thumb.jpg'
            # ffmpeg -ss 00:00:02 -i input -frames:v 1 -q:v 2 -y output.jpg
            subprocess.run(
                ['ffmpeg', '-ss', time, '-i', source_path, '-frames:v', '1', '-q:v', '2', '-y', tmp_out],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            with open(tmp_out, 'rb') as f:
                data = f.read()
            os.remove(tmp_out)
            return ContentFile(data, name=f'{self.id}_thumb.jpg')
        except Exception:
            return None

    def compute_metadata_and_thumbnail(self, save_obj=False):
        """
        Reads file / external URL and populates: sha256, mime_type, size, width/height, thumbnail.
        For images: uses Pillow. For videos: attempts ffmpeg to grab frame.
        """
        changed = False

        if self.file:
            # NOTE: default_storage.open handles S3/local correctly
            with self.file.open('rb') as f:
                # hash
                new_hash = self._compute_hash(f)
                if self.sha256 != new_hash:
                    self.sha256 = new_hash
                    changed = True

                # size & mime
                try:
                    f.seek(0, os.SEEK_END)
                    size = f.tell()
                except Exception:
                    size = None
                if size and self.size != size:
                    self.size = size
                    changed = True

                mime = self._guess_mime(self.file.name)
                if mime and self.mime_type != mime:
                    self.mime_type = mime
                    changed = True

                # If image — thumbnail via PIL
                if self.type == self.TYPE_IMAGE or (mime and mime.startswith('image')):
                    try:
                        f.seek(0)
                        img = Image.open(f)
                        img.load()
                        w, h = img.size
                        if self.width != w or self.height != h:
                            self.width, self.height = w, h
                            changed = True
                        # generate thumbnail and save to self.thumbnail
                        thumb = self._generate_image_thumbnail(img)
                        self.thumbnail.save(thumb.name, thumb, save=False)
                        changed = True
                    except Exception:
                        pass

                # If video — attempt frame grab if ffmpeg available
                elif self.type == self.TYPE_VIDEO or (mime and mime.startswith('video')):
                    # try get basic metadata using ffprobe (optional, not required)
                    # For now attempt to produce a thumbnail by copying to a temp path
                    try:
                        # Save to temp path (default_storage may not give a local path)
                        local_temp = f'/tmp/{self.id}_asset'
                        with open(local_temp, 'wb') as outf:
                            f.seek(0)
                            outf.write(f.read())
                        thumb_cf = self._attempt_video_frame(local_temp)
                        if thumb_cf:
                            self.thumbnail.save(thumb_cf.name, thumb_cf, save=False)
                            changed = True
                        os.remove(local_temp)
                    except Exception:
                        pass

        # if external_url only — metadata left mostly blank; thumbnail could be set by admin or by fetcher
        if save_obj and changed:
            self.save()
        return changed

    def admin_thumbnail_tag(self):
        if self.thumbnail:
            return mark_safe(f'<img src="{self.thumbnail.url}" style="max-height:60px; max-width:120px; object-fit:cover" />')
        if self.file and (self.type == self.TYPE_IMAGE):
            try:
                return mark_safe(f'<img src="{self.file.url}" style="max-height:60px; max-width:120px; object-fit:cover" />')
            except Exception:
                return '(no thumb)'
        return '(no thumb)'
    admin_thumbnail_tag.short_description = 'Thumb'

# Collections for galleries
class AssetCollection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    assets = models.ManyToManyField(Asset, through='AssetCollectionItem', related_name='collections')

    def __str__(self):
        return self.title

class AssetCollectionItem(models.Model):
    collection = models.ForeignKey(AssetCollection, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    caption = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['order']
        unique_together = [('collection', 'asset')]

# Event integration: per-event join model (replaces per-event file storage)
# Place in events app normally; included here for reference.
class EventAsset(models.Model):
    event_id = models.UUIDField()  # replace with ForeignKey to your Event model in actual app
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='event_usages')
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    # optionally store per-event crop coords or display variants
    per_event_meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['order']
        # create a real ForeignKey to Event in your app - this is placeholder
