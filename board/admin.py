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

from . import admin_rehearsal


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


# in board/admin.py (Event admin section)
from django.urls import reverse
from django.utils.html import format_html
from .rehearsal_notes import RehearsalDetails

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_date", "rehearsal_link")

    def rehearsal_link(self, obj):
        details, created = RehearsalDetails.objects.get_or_create(event=obj)
        url = reverse("admin:board_rehearsaldetails_change", args=[details.pk])
        return format_html('<a class="button" href="{}">Open Rehearsal Notes</a>', url)

    rehearsal_link.short_description = "Rehearsal Details"



from django.contrib import admin
from .models import BoardMessage

@admin.register(BoardMessage)
class BoardMessageAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "column", "created_at")
    search_fields = ("title", "content", "author__username")
    list_filter = ("column",)
    autocomplete_fields = ("author",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "column":
            # ✅ Only allow attaching messages to general columns
            kwargs["queryset"] = BoardColumn.objects.filter(column_type="general")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
    search_fields = ("name",)   # 🔹 this is the missing piece


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

'''
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

    '''

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "position")
    list_editable = ("position",)
    ordering = ("position",)

from django import forms
from django.contrib import admin
from .models import Event
from assets.widgets import AssetChooserWidget  # ✅ custom widget we made earlier
from tinymce.widgets import TinyMCE


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
            "rich_description": TinyMCE(attrs={"cols": 80, "rows": 20}),
            "rich_notes": TinyMCE(attrs={"style": "height: 100px; width: 95%;"}),
            # gallery_assets uses the explicit field above
        }


from django.contrib import admin
from .rehearsal_notes import (
    RehearsalDetails,
    RehearsalSection,
    SongRehearsalNote,
)
'''
@admin.register(RehearsalDetails)
class RehearsalDetailsAdmin(admin.ModelAdmin):
    list_display = ("event",)
    search_fields = ("event__title",)
'''
    

@admin.register(RehearsalSection)
class RehearsalSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "rehearsal", "order", "created_by")
    list_filter = ("rehearsal__event__event_date",)
    search_fields = ("title", "body")

@admin.register(SongRehearsalNote)
class SongRehearsalNoteAdmin(admin.ModelAdmin):
    list_display = ("song", "section", "created_by", "created_at")
    list_filter = ("section__rehearsal__event__event_date", "created_by")
    search_fields = ("song__title", "notes")


