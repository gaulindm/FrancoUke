# forms.py
from django import forms
from taggit.models import Tag

class TagFilterForm(forms.Form):
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        label='Select Tag',
        required=True
    )

class SongForm(forms.Form):
    artist = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Artist Name", "class": "form-control"}),
        label="Artist"
    )
    title = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Song Title", "class": "form-control"}),
        label="Title"
    )
    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"placeholder": "Paste your song content here", "class": "form-control", "rows": 10}),
        label="Content"
    )

from .models import SongFormatting

from django import forms
import json
from .models import SongFormatting

class SongFormattingForm(forms.ModelForm):
    class Meta:
        model = SongFormatting
        fields = ["intro", "verse", "chorus", "bridge", "interlude", "outro"]
        widgets = {
            "intro": forms.Textarea(attrs={"rows": 2, "cols": 50}),
            "verse": forms.Textarea(attrs={"rows": 2, "cols": 50}),
            "chorus": forms.Textarea(attrs={"rows": 2, "cols": 50}),
            "bridge": forms.Textarea(attrs={"rows": 2, "cols": 50}),
            "interlude": forms.Textarea(attrs={"rows": 2, "cols": 50}),
            "outro": forms.Textarea(attrs={"rows": 2, "cols": 50}),
        }

    def clean(self):

        cleaned_data = super().clean()
        
        for field_name in self.fields:
            value = cleaned_data.get(field_name, "")

            # ✅ Ensure the value is a string before processing
            if isinstance(value, str):
                value = value.strip()

            # ✅ If the field is empty, explicitly save `{}` instead of `None`
            if value == "" or value is None:
                cleaned_data[field_name] = {}  # ✅ Ensure `{}` is stored
            else:
                try:
                    if isinstance(value, str):  # ✅ Convert only if value is a string
                        cleaned_data[field_name] = json.loads(value)  
                except json.JSONDecodeError:
                    self.add_error(field_name, "Invalid JSON format. Check for missing commas or brackets.")

        return cleaned_data