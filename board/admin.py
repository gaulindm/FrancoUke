from django.contrib import admin
from .models import BoardColumn, BoardItem

class BoardItemInline(admin.TabularInline):
    model = BoardItem
    extra = 1
    fields = ['title', 'description', 'position', 'youtube_url', 'link', 'media_file', 'event_date']
from django.contrib import admin
from .models import BoardColumn, BoardItem, RehearsalAvailability



class RehearsalAvailabilityInline(admin.TabularInline):
    model = RehearsalAvailability
    extra = 0
    readonly_fields = ['user', 'updated_at']
    can_delete = False


@admin.register(BoardColumn)
class BoardColumnAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'is_public']
    list_editable = ['position', 'is_public']
    ordering = ['position']


@admin.register(BoardItem)
class BoardItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'column', 'is_rehearsal', 'event_date', 'position']
    list_filter = ['is_rehearsal', 'column']
    search_fields = ['title', 'description', 'rich_description', 'location']
    ordering = ['column__position', 'position']
    inlines = [RehearsalAvailabilityInline]

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
