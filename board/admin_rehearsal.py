# board/admin_rehearsal.py
from django import forms
from django.contrib import admin
import nested_admin

from .rehearsal_notes import (
    RehearsalDetails,
    RehearsalSection,
    SongRehearsalNote,
)


# ---- Forms ----

from django import forms
from tinymce.widgets import TinyMCE  # ✅ replace CKEditor
from .rehearsal_notes import RehearsalDetails, RehearsalSection, SongRehearsalNote


# 🎨 Shared TinyMCE config for all rich text fields
TINY_SIMPLE_CONFIG = {
    "menubar": False,
    "plugins": "link lists",
    "toolbar": "undo redo | bold italic underline | bullist numlist | "
               "alignleft aligncenter alignright | link",
    "height": 250,
}


class RehearsalDetailsForm(forms.ModelForm):
    class Meta:
        model = RehearsalDetails
        fields = "__all__"
        widgets = {
            "notes": TinyMCE(attrs={"cols": 80, "rows": 10}, mce_attrs=TINY_SIMPLE_CONFIG),
        }


class RehearsalSectionForm(forms.ModelForm):
    class Meta:
        model = RehearsalSection
        fields = "__all__"
        widgets = {
            "body": TinyMCE(attrs={"cols": 80, "rows": 10}, mce_attrs=TINY_SIMPLE_CONFIG),
        }


class SongRehearsalNoteForm(forms.ModelForm):
    class Meta:
        model = SongRehearsalNote
        fields = "__all__"
        widgets = {
            "notes": TinyMCE(attrs={"cols": 80, "rows": 10}, mce_attrs=TINY_SIMPLE_CONFIG),
        }


# ---- Nested Inlines ----

class SongRehearsalNoteInline(nested_admin.NestedTabularInline):
    model = SongRehearsalNote
    autocomplete_fields = ["song"]
    extra = 0

class RehearsalSectionInline(nested_admin.NestedStackedInline):
    model = RehearsalSection
    inlines = [SongRehearsalNoteInline]
    extra = 0


# ---- Main Admin ----

@admin.register(RehearsalDetails)
class RehearsalDetailsAdmin(nested_admin.NestedModelAdmin):
    form = RehearsalDetailsForm
    inlines = [RehearsalSectionInline]
    list_display = ("event", "event_date", "created_at")
    readonly_fields = ("created_at",)
    search_fields = ("event__title",)

    def event_date(self, obj):
        return obj.event.event_date if obj.event else None
    event_date.short_description = "Event Date"