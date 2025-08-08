from django.contrib import admin
from .models import BoardColumn, BoardItem, BoardItemPhoto, RehearsalAvailability

# Inline: Photos
class BoardItemPhotoInline(admin.TabularInline):
    model = BoardItemPhoto
    extra = 1
    fields = ['image', 'uploaded_at']
    readonly_fields = ['uploaded_at']

# Optional: Show thumbnail in admin
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 100px;" />', obj.image.url)
        return ""

# Inline: Rehearsal availability
class RehearsalAvailabilityInline(admin.TabularInline):
    model = RehearsalAvailability
    extra = 0
    readonly_fields = ['user', 'updated_at']
    can_delete = False

# BoardItem Admin: Merged version
@admin.register(BoardItem)
class BoardItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'column', 'is_rehearsal', 'event_date', 'position']
    list_filter = ['is_rehearsal', 'column']
    search_fields = ['title', 'description', 'rich_description', 'location']
    ordering = ['column__position', 'position']
    inlines = [BoardItemPhotoInline, RehearsalAvailabilityInline]

    fieldsets = (
        (None, {
            'fields': (
                'title', 'column', 'position', 'is_rehearsal'
            )
        }),
        ('Schedule & Location', {
            'fields': (
                'event_date', 'location'
            ),
            'classes': ('collapse',)
        }),
        ('Descriptions', {
            'fields': (
                'description', 'rich_description'
            )
        }),
        ('Media & Links', {
            'fields': (
                'youtube_url', 'link', 'media_file'
            ),
            'classes': ('collapse',)
        }),
    )

@admin.register(BoardColumn)
class BoardColumnAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'is_public', 'column_type']
    list_editable = ['position', 'is_public', 'column_type']
    ordering = ['position']
