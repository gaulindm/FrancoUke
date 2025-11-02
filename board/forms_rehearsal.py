from django import forms
from django.forms import inlineformset_factory
from tinymce.widgets import TinyMCE

from .rehearsal_notes import RehearsalDetails, SongRehearsalNote


class RehearsalDetailsForm(forms.ModelForm):
    """Form for editing general rehearsal notes."""
    class Meta:
        model = RehearsalDetails
        fields = ["notes"]
        widgets = {
            "notes": TinyMCE(
                attrs={"cols": 80, "rows": 15},
                mce_attrs={
                    "menubar": False,
                    "plugins": "link lists",
                    "toolbar": "undo redo | bold italic underline | bullist numlist | alignleft aligncenter alignright | link",
                    "height": 300,
                },
            ),
        }


class SongRehearsalNoteForm(forms.ModelForm):
    """Form for editing per-song rehearsal notes."""
    class Meta:
        model = SongRehearsalNote
        fields = ["song", "notes"]
        widgets = {
            "song": forms.TextInput(attrs={
                "readonly": "readonly",
                "class": "form-control-plaintext"
            }),
            "notes": TinyMCE(
                attrs={"cols": 80, "rows": 6},
                mce_attrs={
                    "menubar": False,
                    "plugins": "link lists",
                    "toolbar": "undo redo | bold italic underline | bullist numlist | alignleft aligncenter alignright | link",
                    "height": 200,
                },
            ),
        }


SongRehearsalNoteFormSet = inlineformset_factory(
    RehearsalDetails,
    SongRehearsalNote,
    form=SongRehearsalNoteForm,
    extra=0,
    can_delete=False,
)
