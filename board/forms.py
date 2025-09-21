# board/forms.py
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import BoardMessage

class BoardMessageForm(forms.ModelForm):
    class Meta:
        model = BoardMessage
        fields = ["title", "content"]  # author handled automatically
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": CKEditorWidget(config_name="simple"),
        }
