from django import forms
from django.contrib import admin
import nested_admin
from tinymce.widgets import TinyMCE
from django.db.models import Count, Max

from .rehearsal_notes import (
    RehearsalDetails,
    SongRehearsalNote,
)
from songbook.models import Song


# 🎨 TinyMCE shared config
TINY_SIMPLE_CONFIG = {
    "menubar": False,
    "plugins": "link lists",
    "toolbar": (
        "undo redo | formatselect | bold italic underline | bullist numlist outdent indent lineheight| "
        "alignleft aligncenter alignright "
    ),
    "height": 300,
}


# ---- Forms ----

class RehearsalDetailsForm(forms.ModelForm):
    class Meta:
        model = RehearsalDetails
        fields = "__all__"
        widgets = {
            "notes": TinyMCE(attrs={"cols": 80, "rows": 10}, mce_attrs=TINY_SIMPLE_CONFIG),
        }


class SongRehearsalNoteForm(forms.ModelForm):
    class Meta:
        model = SongRehearsalNote
        fields = "__all__"
        widgets = {
            "notes": TinyMCE(attrs={"cols": 80, "rows": 5}, mce_attrs=TINY_SIMPLE_CONFIG),
        }


# ---- Inline ----

class SongRehearsalNoteInline(nested_admin.NestedStackedInline):
    model = SongRehearsalNote
    form = SongRehearsalNoteForm
    autocomplete_fields = ["song"]
    extra = 0
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("song", "notes", ("created_by", "created_at"))}),
    )


# ---- Main Admin (Editable) ----

@admin.register(RehearsalDetails)
class RehearsalDetailsAdmin(nested_admin.NestedModelAdmin):
    form = RehearsalDetailsForm
    inlines = [SongRehearsalNoteInline]

    list_display = ("event", "event_date", "created_at")
    readonly_fields = ("created_at",)
    search_fields = ("event__title",)

    def event_date(self, obj):
        return obj.event.event_date if obj.event else None
    event_date.short_description = "Event Date"


# ---- Read-only Songs with Rehearsal Notes ----

class SongsWithRehearsalNotesAdmin(admin.ModelAdmin):
    list_display = ("songTitle", "rehearsal_notes_count", "last_rehearsed_at")
    search_fields = ("songTitle",)
    ordering = ("songTitle",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Annotate with rehearsal note stats
        return (
            qs.annotate(
                rehearsal_notes_count=Count("rehearsal_notes", distinct=True),
                last_rehearsed_at=Max("rehearsal_notes__rehearsal__event__event_date"),
            )
            .filter(rehearsal_notes_count__gt=0)
        )

    def rehearsal_notes_count(self, obj):
        return obj.rehearsal_notes_count
    rehearsal_notes_count.short_description = "Rehearsal Notes"

    def last_rehearsed_at(self, obj):
        return obj.last_rehearsed_at
    last_rehearsed_at.short_description = "Last Rehearsal Date"

    # 🚫 Make everything read-only
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register as a proxy model so we don’t override the main Song admin
class SongWithRehearsalNotes(Song):
    class Meta:
        proxy = True
        verbose_name = "Song with Rehearsal Notes"
        verbose_name_plural = "Songs with Rehearsal Notes"


admin.site.register(SongWithRehearsalNotes, SongsWithRehearsalNotesAdmin)
