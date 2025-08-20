from django.contrib import admin
from .models import BoardColumn, BoardItem, BoardItemPhoto, RehearsalAvailability
from .models import Performance, BoardItemPhoto, Event, PerformanceDetails, EventPhoto



# Inline for PerformanceDetails (inside Event)
class PerformanceDetailsInline(admin.StackedInline):
    model = PerformanceDetails
    extra = 0
    show_change_link = True




class EventInline(admin.StackedInline):
    model = Event
    extra = 0   # don’t show extra empty forms by default
    show_change_link = True  # show link to full Event page
    autocomplete_fields = ("board_item",)  # nice search UI




@admin.register(BoardItem)
class BoardItemAdmin(admin.ModelAdmin):
    list_display = ("title", "column", "created_at", "position")
    search_fields = ("title", "description")
    inlines = [EventInline]   # ✅ attach events inline




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

class EventPhotoInline(admin.TabularInline):
    model = EventPhoto
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "status", "event_date", "start_time", "location", "board_item")
    list_filter = ("event_type", "status", "event_date")
    search_fields = ("title", "description", "location", "board_item__title")
    date_hierarchy = "event_date"
    inlines = [PerformanceDetailsInline, EventPhotoInline]
    autocomplete_fields = ("board_item",)

# Keep your existing registrations for BoardItem, BoardColumn, etc.
# Example:
@admin.register(BoardItemPhoto)
class BoardItemPhotoAdmin(admin.ModelAdmin):
    list_display = ("board_item", "is_cover", "uploaded_at")
    list_filter = ("is_cover",)



class BoardItemPhotoInline(admin.TabularInline):
    model = BoardItemPhoto
    extra = 1

'''
@admin.register(BoardItem)
class BoardItemAdmin(admin.ModelAdmin):
    list_display = ("title", "column", "created_at")
    list_filter = ("column__column_type",)
    search_fields = ("title", "description")
    ordering = ("position", "created_at")

    inlines = [PerformanceInline, BoardItemPhotoInline]
'''

@admin.register(BoardColumn)
class BoardColumnAdmin(admin.ModelAdmin):
    list_display = ("name", "column_type", "position", "is_public")
    list_editable = ("position", "is_public")
    ordering = ("position",)


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ("board_item", "performance_type", "event_date", "start_time", "location", "is_rehearsal")
    list_filter = ("performance_type", "is_rehearsal")
    search_fields = ("board_item__title", "location")

'''
@admin.register(BoardItemPhoto)
class BoardItemPhotoAdmin(admin.ModelAdmin):
    list_display = ("board_item", "is_cover", "uploaded_at")
    list_filter = ("is_cover",)
'''

@admin.register(RehearsalAvailability)
class RehearsalAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("user", "performance", "status", "updated_at")
    list_filter = ("status", "performance__is_rehearsal")
    search_fields = ("user__username", "performance__board_item__title")






# Inline: Rehearsal availability
class RehearsalAvailabilityInline(admin.TabularInline):
    model = RehearsalAvailability
    extra = 0
    readonly_fields = ['user', 'updated_at']
    can_delete = False


