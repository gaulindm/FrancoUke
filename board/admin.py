from django import forms
#from .forms import EventForm

from django.contrib import admin
from assets.models import Asset
from django.utils import timezone

from .models import Event
from assets.widgets import AssetChooserWidget, AssetGalleryChooserWidget
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

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"
        widgets = {
            "cover_asset": AssetChooserWidget(),  # 👈 your chooser widget
        }



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

# board/admin.py
from django.contrib import admin
from django.utils import timezone
from .models import Event, EventAvailability, EventPhoto


class EventAvailabilityInline(admin.TabularInline):
    model = EventAvailability
    extra = 1


class EventPhotoInline(admin.TabularInline):
    model = EventPhoto
    extra = 1
    fields = ("image", "is_cover", "uploaded_at")
    readonly_fields = ("uploaded_at",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventForm
    #filter_horizontal = ("gallery_assets",)

    list_display = (
        "title",
        "event_type",
        "status",
        "event_date",
        "start_time",
        "end_time",
        "venue",
        "arrive_by",
        "chairs",
        "attire",
        "column",   # ✅ new column field for board placement
    )
    list_filter = ("event_type", "status", "venue", "column")
    search_fields = ("title", "rich_description", "location")
    ordering = ("event_date", "start_time")

    fieldsets = (
        (None, {
            "fields": ("title", "rich_description", "event_type", "status","cover_asset","gallery_assets")
        }),
        ("Scheduling", {
            "fields": ("event_date", "start_time", "end_time", "arrive_by", "chairs", "attire", "location")
        }),
        ("Associations", {
            "fields": ("venue", "column"),
            "description": "Link this event either to a Venue (recurring events) or to a Board Column (e.g., Upcoming, To Be Confirmed, Past)."
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    readonly_fields = ("created_at", "updated_at")
    inlines = [EventAvailabilityInline, EventPhotoInline]

    # ✅ Custom action to duplicate selected events
    actions = ["duplicate_events"]

    def duplicate_events(self, request, queryset):
        count = 0
        for event in queryset:
            event.pk = None  # remove primary key so Django creates a new row
            event.title = f"{event.title} (Copy)"  # optional tweak
            event.created_at = timezone.now()
            event.updated_at = timezone.now()
            event.save()
            count += 1
        self.message_user(request, f"✅ Successfully duplicated {count} event(s).")

    duplicate_events.short_description = "Duplicate selected events"

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "position")
    list_editable = ("position",)
    ordering = ("position",)

from django import forms
from django.contrib import admin
from .models import Event
from assets.widgets import AssetChooserWidget  # ✅ custom widget we made earlier

class EventAdminForm(forms.ModelForm):
    gallery_assets = forms.ModelMultipleChoiceField(
        queryset=Asset.objects.all(),
        required=False,
        widget=AssetGalleryChooserWidget()
    )

    class Meta:
        model = Event
        fields = "__all__"
        widgets = {
            "cover_asset": AssetChooserWidget(),
            # gallery_assets uses the explicit field above
        }
