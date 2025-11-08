# board/forms_rehearsal.py
from django import forms
from django.forms import inlineformset_factory
from tinymce.widgets import TinyMCE
from .models import RehearsalDetails, SongRehearsalNote


class RehearsalDetailsForm(forms.ModelForm):
    class Meta:
        model = RehearsalDetails
        fields = ["notes"]
        widgets = {
            "notes": TinyMCE(
                attrs={"cols": 80, "rows": 10},
                mce_attrs={
                    "menubar": False,
                    "plugins": "link lists",
                    "toolbar": "undo redo | bold italic underline | bullist numlist | alignleft aligncenter alignright | link",
                    "height": 300,
                },
            )
        }


from django import forms
from django.forms import inlineformset_factory
from tinymce.widgets import TinyMCE
from songbook.models import Song
from .models import RehearsalDetails, SongRehearsalNote


class SongRehearsalNoteForm(forms.ModelForm):
    class Meta:
        model = SongRehearsalNote
        fields = ["song", "notes"]
        widgets = {
            "song": forms.Select(
                attrs={"class": "form-select select2-song", "data-placeholder": "Select a song..."}
            ),
            "notes": TinyMCE(
                attrs={"cols": 80, "rows": 5},
                mce_attrs={
                    "menubar": False,
                    "plugins": "link lists",
                    "toolbar": "undo redo | bold italic underline | bullist numlist | alignleft aligncenter alignright | link",
                    "height": 200,
                },
            ),
        }


'''
# ✅ Define the formset AFTER defining the form
SongRehearsalNoteFormSet = inlineformset_factory(
    RehearsalDetails,
    SongRehearsalNote,
    form=SongRehearsalNoteForm,
    extra=1,
    can_delete=True,
)
'''