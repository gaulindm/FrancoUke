# assets/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Asset, Tag, AssetCollection, AssetCollectionItem
from assets.widgets import AssetChooserWidget  # ✅ your chooser widget

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('admin_thumbnail_tag', 'title', 'type', 'uploaded_at', 'is_public')
    search_fields = ('title', 'caption', 'sha256')
    list_filter = ('type', 'is_public', 'uploaded_at')
    readonly_fields = ('admin_thumbnail_tag', 'sha256', 'uploaded_at')
    fieldsets = (
        (None, {'fields': ('title', 'caption', 'type', 'provider', 'file', 'external_url', 'thumbnail')}),
        ('Metadata', {'fields': ('mime_type', 'size', 'width', 'height', 'duration', 'sha256', 'is_public')})
    )
    # optionally add actions for bulk making public/private or generating thumbnails
