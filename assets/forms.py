from django import forms
from .models import Asset
from board.models import Event  # adjust path if needed

from .widgets import MultiFileInput  # if you put it in widgets.py

class AssetBulkUploadForm(forms.Form):
    files = forms.FileField(
        widget=MultiFileInput(attrs={"multiple": True}),
        required=True,
        label="Upload Files",
    )
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(),
        required=False,
        label="Attach to Event",
        help_text="Optional: assign uploaded files to an event’s gallery",
    )
    tags = forms.CharField(
        required=False,
        label="Tags",
        help_text="Comma-separated tags to apply to uploaded assets",
    )
