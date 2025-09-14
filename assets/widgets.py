# assets/widgets.py
from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from .models import Asset
from django.forms.widgets import ClearableFileInput


class AssetChooserWidget(forms.TextInput):
    template_name = "assets/widgets/asset_chooser.html"

    class Media:
        js = ("assets/js/asset_chooser.js",)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        asset_url = None
        if value:
            try:
                a = Asset.objects.get(pk=value)
                asset_url = a.thumbnail.url if a.thumbnail else (a.file.url if a.file else "")
            except Asset.DoesNotExist:
                asset_url = None
        context["widget"]["asset_url"] = asset_url
        return context

class AssetGalleryChooserWidget(forms.Widget):
    """
    Widget for selecting multiple assets using the chooser modal.
    Renders a hidden multiple input (list of selected ids will be posted as multiple inputs),
    a preview area, and a "Choose assets" button.
    """
    template_name = "assets/widgets/asset_gallery_chooser.html"

    class Media:
        js = ("assets/js/asset_chooser.js",)

    def __init__(self, attrs=None):
        super().__init__(attrs)

    def format_value(self, value):
        # value might be a queryset, list of pks, or a comma-string
        if value is None:
            return []
        if hasattr(value, "all"):  # queryset
            return [str(v.pk) for v in value.all()]
        if isinstance(value, (list, tuple)):
            return [str(v) for v in value]
        if isinstance(value, str):
            if value == "":
                return []
            return value.split(",")
        return [str(value)]

    def render(self, name, value, attrs=None, renderer=None):
        value_list = self.format_value(value)
        # render using a small template
        context = {
            "name": name,
            "value_list": value_list,
            "preview_urls": [],
            "attrs": attrs or {},
        }
        # gather preview URLs for current values
        previews = []
        for pk in value_list:
            try:
                a = Asset.objects.get(pk=pk)
                previews.append({
                    "id": str(a.pk),
                    "thumb": a.thumbnail.url if a.thumbnail else (a.file.url if a.file else ""),
                })
            except Asset.DoesNotExist:
                pass
        context["preview_urls"] = previews
        html = render_to_string(self.template_name, context)
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        """
        Expect the form submit to include multiple inputs with the same name (e.g. name="gallery_assets")
        or a comma-separated hidden input; support both.
        """
        # Django provides lists for multiple inputs (data.getlist). Use that if present.
        if hasattr(data, "getlist"):
            vals = data.getlist(name)
            # strip empty
            return [v for v in vals if v]
        # fallback single value (maybe comma separated)
        val = data.get(name)
        if not val:
            return []
        if isinstance(val, str) and "," in val:
            return [v for v in val.split(",") if v]
        return [val]
