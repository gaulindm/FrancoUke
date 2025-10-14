# board/admin_rehearsal.py
from django import forms
from django.contrib import admin
from ckeditor.widgets import CKEditorWidget
import nested_admin

from .rehearsal_notes import (
    RehearsalDetails,
    RehearsalSection,
    SongRehearsalNote,
)


# ---- Forms ----

class RehearsalDetailsForm(forms.ModelForm):
    class Meta:
        model = RehearsalDetails
        fields = "__all__"
        widgets = {
            "notes": CKEditorWidget(config_name="default"),
        }


class RehearsalSectionForm(forms.ModelForm):
    class Meta:
        model = RehearsalSection
        fields = "__all__"
        widgets = {
            "body": CKEditorWidget(config_name="default"),
        }


class SongRehearsalNoteForm(forms.ModelForm):
    class Meta:
        model = SongRehearsalNote
        fields = "__all__"
        widgets = {
            "notes": CKEditorWidget(config_name="default"),
        }


# ---- Nested Inlines ----

class SongRehearsalNoteInline(nested_admin.NestedTabularInline):
    model = SongRehearsalNote
    extra = 1

class RehearsalSectionInline(nested_admin.NestedStackedInline):
    model = RehearsalSection
    inlines = [SongRehearsalNoteInline]
    extra = 1


# ---- Main Admin ----

@admin.register(RehearsalDetails)
class RehearsalDetailsAdmin(nested_admin.NestedModelAdmin):
    inlines = [RehearsalSectionInline]
    list_display = ("event", "created_at")  # ✅ uses new field
    readonly_fields = ("created_at",)