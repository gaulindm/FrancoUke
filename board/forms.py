'''# board/forms.py
from django import forms
from assets.models import Asset
from assets.widgets import AssetChooserWidget, AssetGalleryChooserWidget
from .models import Event

class EventAdminForm(forms.ModelForm):
    gallery_assets = forms.ModelMultipleChoiceField(
        queryset=Asset.objects.all(),
        required=False,
        widget=AssetGalleryChooserWidget()
    )

    class Meta:
        model = Event
        fields = "__all__"
        widgets = {
            "cover_asset": AssetChooserWidget(),
        }'''