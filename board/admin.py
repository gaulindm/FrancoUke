from django.contrib import admin
from .models import (
    BoardColumn, BoardItem, BoardItemPhoto,
    Event, EventPhoto, EventAvailability, Venue
)

# -------------------------
# Inlines
# -------------------------
class BoardItemPhotoInline(admin.TabularInline):
    model = BoardItemPhoto
    extra = 1
    fields = ("image", "is_cover", "uploaded_at")
    readonly_fields = ("uploaded_at",)


class EventPhotoInline(admin.TabularInline):
    model = EventPhoto
    extra = 1
    fields = ("image", "is_cover", "uploaded_at")
    readonly_fields = ("uploaded_at",)


class EventAvailabilityInline(admin.TabularInline):
    model = EventAvailability
    extra = 1


# -------------------------
# Admin registrations
# -------------------------
@admin.register(BoardItem)
class BoardItemAdmin(admin.ModelAdmin):
    list_display = ("title", "column", "created_at", "position")
    list_filter = ("column__column_type",)
    search_fields = ("title", "description")
    ordering = ("position", "created_at")
    inlines = [BoardItemPhotoInline]  # ✅ only photos, no performance inline


@admin.register(BoardColumn)
class BoardColumnAdmin(admin.ModelAdmin):
    list_display = ("name", "column_type", "position", "is_public")
    list_editable = ("position", "is_public")
    ordering = ("position",)


@admin.register(BoardItemPhoto)
class BoardItemPhotoAdmin(admin.ModelAdmin):
    list_display = ("board_item", "is_cover", "uploaded_at")
    list_filter = ("is_cover",)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "event_type",
        "status",
        "event_date",
        "start_time",
        "end_time",
        "venue",
        "column",   # ✅ show the new column field
    )
    list_filter = ("event_type", "status", "venue", "column")
    search_fields = ("title", "rich_description", "location")
    ordering = ("event_date", "start_time")

    fieldsets = (
        (None, {
            "fields": ("title", "rich_description", "event_type", "status")
        }),
        ("Scheduling", {
            "fields": ("event_date", "start_time", "end_time", "location")
        }),
        ("Associations", {
            "fields": ("venue", "column"),
            "description": "Link this event either to a Venue (for recurring events) or to a Board Column (e.g., Upcoming, To Be Confirmed, Past)."
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    readonly_fields = ("created_at", "updated_at")
    inlines = [EventAvailabilityInline, EventPhotoInline]

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "position")
    list_editable = ("position",)
    ordering = ("position",)
