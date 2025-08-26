from django.contrib import admin
from .models import (
    BoardColumn, BoardItem, BoardItemPhoto, Performance,
    Event, PerformanceDetails, EventPhoto, Venue
)

# -------------------------
# Inlines
# -------------------------
class PerformanceDetailsInline(admin.StackedInline):
    model = PerformanceDetails
    extra = 0
    max_num = 1
    fieldsets = (
        ("Performance Logistics", {
            "fields": ("attire", "chairs", "arrive_by")
        }),
    )


class PerformanceInline(admin.StackedInline):
    model = Performance
    extra = 0
    max_num = 1  # only one performance per BoardItem
    fieldsets = (
        ("Event Details", {
            "fields": ("performance_type", "event_date", "start_time", "end_time", "arrive_by", "location")
        }),
        ("Logistics", {
            "fields": ("attire", "chairs", "is_rehearsal")
        }),
    )


class EventInline(admin.StackedInline):
    model = Event
    extra = 0
    show_change_link = True
    autocomplete_fields = ("board_item",)


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


# -------------------------
# Admin registrations
# -------------------------
@admin.register(BoardItem)
class BoardItemAdmin(admin.ModelAdmin):
    list_display = ("title", "column", "created_at", "position")
    list_filter = ("column__column_type",)
    search_fields = ("title", "description")
    ordering = ("position", "created_at")
    inlines = [PerformanceInline, EventInline, BoardItemPhotoInline]  # ✅ now includes photos


@admin.register(BoardColumn)
class BoardColumnAdmin(admin.ModelAdmin):
    list_display = ("name", "column_type", "position", "is_public")
    list_editable = ("position", "is_public")
    ordering = ("position",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "status", "event_date", "start_time", "location", "board_item")
    list_filter = ("event_type", "status", "event_date")
    search_fields = ("title", "description", "location", "board_item__title")
    date_hierarchy = "event_date"
    inlines = [PerformanceDetailsInline, EventPhotoInline]
    autocomplete_fields = ("board_item",)


@admin.register(BoardItemPhoto)
class BoardItemPhotoAdmin(admin.ModelAdmin):
    list_display = ("board_item", "is_cover", "uploaded_at")
    list_filter = ("is_cover",)


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ("board_item", "performance_type", "event_date", "start_time", "location", "is_rehearsal")
    list_filter = ("performance_type", "is_rehearsal")
    search_fields = ("board_item__title", "location")


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "position")
    list_editable = ("position",)
    ordering = ("position",)
