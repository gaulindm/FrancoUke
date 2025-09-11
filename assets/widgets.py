from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from .models import Asset

class AssetChooserWidget(forms.TextInput):
    template_name = "assets/widgets/asset_chooser.html"

    class Media:
        js = ("assets/js/asset_chooser.js",)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        asset_url = None
        if value:
            try:
                asset = Asset.objects.get(pk=value)
                asset_url = asset.thumbnail.url if asset.thumbnail else asset.file.url
            except Asset.DoesNotExist:
                pass
        context["widget"]["asset_url"] = asset_url
        return context

