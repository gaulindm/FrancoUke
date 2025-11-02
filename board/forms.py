#board/forms.py
from django import forms
from tinymce.widgets import TinyMCE  # ✅ replace CKEditorWidget
from .models import BoardMessage


class BoardMessageForm(forms.ModelForm):
    class Meta:
        model = BoardMessage
        fields = ["title", "content"]  # author handled automatically
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": TinyMCE(
                attrs={"cols": 80, "rows": 10},  # ✅ set editor size
                mce_attrs={
                    "menubar": False,
                    "plugins": "link lists",
                    "toolbar": "undo redo | bold italic underline | bullist numlist | alignleft aligncenter alignright | link",
                    "height": 250,  # pixels
                },
            ),
        }
