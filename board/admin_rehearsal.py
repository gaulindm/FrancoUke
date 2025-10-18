from django import forms
from django.contrib import admin
import nested_admin
from tinymce.widgets import TinyMCE

from .rehearsal_notes import (
    RehearsalDetails,
    SongRehearsalNote,
)


# 🎨 TinyMCE shared config
TINY_SIMPLE_CONFIG = {
    "menubar": False,
    "plugins": "link lists",
    "toolbar": (
        "undo redo | bold italic underline | bullist numlist | "
        "alignleft aligncenter alignright | link"
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
            "notes": TinyMCE(attrs={"cols": 80, "rows": 10}, mce_attrs=TINY_SIMPLE_CONFIG),
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


# ---- Main Admin ----

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
