# board/admin.py
from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from tinymce.widgets import TinyMCE
from assets.models import Asset
from assets.widgets import AssetChooserWidget, AssetGalleryChooserWidget

from .models import (
    BoardColumn,
    BoardItem,
    BoardItemPhoto,
    BoardMessage,
    Event,
    EventPhoto,
    EventAvailability,
    Venue,
)
from .rehearsal_notes import (
    RehearsalDetails,
    RehearsalSection,
    SongRehearsalNote,
)

# ------------------------------------------------------------
# 🧩 INLINE CLASSES
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# 🏠 BOARD & COLUMN ADMINS
# ------------------------------------------------------------

@admin.register(BoardColumn)
class BoardColumnAdmin(admin.ModelAdmin):
    list_display = ("name", "column_type", "position", "is_public")
    list_editable = ("position", "is_public")
    search_fields = ("name",)
    ordering = ("position",)


@admin.register(BoardItem)
class BoardItemAdmin(admin.ModelAdmin):
    list_display = ("title", "column", "created_at", "position")
    list_filter = ("column__column_type",)
    search_fields = ("title", "description")
    ordering = ("position", "created_at")
    inlines = [BoardItemPhotoInline]


@admin.register(BoardItemPhoto)
class BoardItemPhotoAdmin(admin.ModelAdmin):
    list_display = ("board_item", "is_cover", "uploaded_at")
    list_filter = ("is_cover",)


# ------------------------------------------------------------
# 💬 BOARD MESSAGES (Leaders only)
# ------------------------------------------------------------

@admin.register(BoardMessage)
class BoardMessageAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "column", "created_at")
    search_fields = ("title", "content", "author__username")
    list_filter = ("column",)
    autocomplete_fields = ("author",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "column":
            kwargs["queryset"] = BoardColumn.objects.filter(column_type="general")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ------------------------------------------------------------
# 🎵 EVENT ADMIN
# ------------------------------------------------------------

class EventAdminForm(forms.ModelForm):
    """Custom admin form for Event with chooser and TinyMCE widgets."""
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
        }


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Event management with media inlines, duplication, and rehearsal link."""
    form = EventAdminForm

    list_display = ("title", "event_type", "status", "event_date", "venue", "column", "rehearsal_link")
    list_filter = ("event_type", "status", "venue", "column")
    search_fields = ("title", "rich_description", "location")
    ordering = ("event_date", "start_time")
    readonly_fields = ("created_at", "updated_at")
    inlines = [EventAvailabilityInline, EventPhotoInline]
    actions = ["duplicate_events"]

    fieldsets = (
        (None, {
            "fields": ("title", "event_type", "status", "cover_asset", "gallery_assets", "rich_description")
        }),
        ("Scheduling", {
            "fields": ("event_date", "start_time", "end_time", "arrive_by", "chairs", "attire", "location")
        }),
        ("Associations", {
            "fields": ("venue", "column"),
            "description": "Link event to a Venue (recurring) or Board Column (Upcoming, Past, etc.)"
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    # --------------------------------------------------------
    # Custom admin methods
    # --------------------------------------------------------

    def rehearsal_link(self, obj):
        """Shortcut button to open related rehearsal notes."""
        details, _ = RehearsalDetails.objects.get_or_create(event=obj)
        url = reverse("admin:board_rehearsaldetails_change", args=[details.pk])
        return format_html('<a class="button" href="{}">Rehearsal Notes</a>', url)
    rehearsal_link.short_description = "Rehearsal"

    def duplicate_events(self, request, queryset):
        """Admin action: duplicate selected events."""
        count = 0
        for event in queryset:
            event.pk = None
            event.title = f"{event.title} (Copy)"
            event.created_at = timezone.now()
            event.updated_at = timezone.now()
            event.save()
            count += 1
        self.message_user(request, f"✅ Duplicated {count} event(s).")
    duplicate_events.short_description = "Duplicate selected events"


# ------------------------------------------------------------
# 🏛️ VENUE ADMIN
# ------------------------------------------------------------

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "position")
    list_editable = ("position",)
    ordering = ("position",)


# ------------------------------------------------------------
# 🧾 REHEARSAL ADMIN
# ------------------------------------------------------------

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

@admin.register(RehearsalDetails)
class RehearsalDetailsAdmin(admin.ModelAdmin):
    list_display = ("event", "created_at")
    search_fields = ("event__title",)
