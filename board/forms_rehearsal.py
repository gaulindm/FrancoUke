# board/forms_rehearsal.py
from django import forms
from songs.models import Song
from .rehearsal_notes import RehearsalSection

class RehearsalSectionForm(forms.ModelForm):
    class Meta:
        model = RehearsalSection
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Only include StrumSphere songs
        self.fields["song"].queryset = Song.objects.filter(site_name="StrumSphere").order_by("songTitle")
