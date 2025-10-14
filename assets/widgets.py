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

        # 🩹 Fix: avoid "None" strings or invalid UUIDs
        if value and str(value).lower() != "none":
            try:
                a = Asset.objects.get(pk=value)
                asset_url = a.thumbnail.url if a.thumbnail else (a.file.url if a.file else "")
            except (Asset.DoesNotExist, ValueError, TypeError):
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
            if value.strip() in ("", "None"):
                return []
            return value.split(",")
        return [str(value)]

    def render(self, name, value, attrs=None, renderer=None):
        value_list = self.format_value(value)

        context = {
            "name": name,
            "value_list": value_list,
            "preview_urls": [],
            "attrs": attrs or {},
        }

        # 🩹 Fix: safely resolve assets
        previews = []
        for pk in value_list:
            if not pk or str(pk).lower() == "none":
                continue
            try:
                a = Asset.objects.get(pk=pk)
                previews.append({
                    "id": str(a.pk),
                    "thumb": a.thumbnail.url if a.thumbnail else (a.file.url if a.file else ""),
                })
            except (Asset.DoesNotExist, ValueError, TypeError):
                pass

        context["preview_urls"] = previews
        html = render_to_string(self.template_name, context)
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        """
        Expect multiple inputs or a comma-separated hidden input.
        """
        if hasattr(data, "getlist"):
            vals = data.getlist(name)
            return [v for v in vals if v and str(v).lower() != "none"]

        val = data.get(name)
        if not val:
            return []
        if isinstance(val, str) and "," in val:
            return [v for v in val.split(",") if v and str(v).lower() != "none"]
        return [val] if val and str(val).lower() != "none" else []
