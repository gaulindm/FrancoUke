# board/forms.py
from django import forms
from assets.widgets import AssetChooserWidget
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"
        widgets = {
            "cover_asset": AssetChooserWidget(),
        }