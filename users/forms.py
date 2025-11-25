from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import UserPreference
from songbook.utils.chord_library import load_chord_dict

User = get_user_model()


class BootstrapFormMixin:
    """Apply Bootstrap 5 classes to all form fields."""

    def apply_bootstrap_classes(self):
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.update({"class": "form-check-input"})
            elif isinstance(widget, forms.Select):
                widget.attrs.update({"class": "form-select"})
            else:
                widget.attrs.update({"class": "form-control"})


class CustomUserCreationForm(UserCreationForm, BootstrapFormMixin):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_classes()


class UserRegisterForm(UserCreationForm, BootstrapFormMixin):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_classes()

from songbook.utils.chord_library import load_chord_dict
from teleprompter.views import clean_chord_name


# users/forms.py
from django import forms
from .models import UserPreference
from songbook.utils.chord_utils import load_chords  # <- ensure this import exists
# keep BootstrapFormMixin import as-is

# users/forms.py
from django import forms
from .models import UserPreference

from django import forms
from .models import UserPreference

class UserPreferenceForm(forms.ModelForm):
    # Text field for comma-separated known chords
    known_chords_text = forms.CharField(
        required=False,
        label="Known Chords",
        widget=forms.TextInput(attrs={"placeholder": "C, F, G7"}),
        help_text="Enter your known chords separated by commas (e.g., C, F, G7)."
    )

    class Meta:
        model = UserPreference
        fields = [
            "primary_instrument",
            "secondary_instrument",
            "is_lefty",
            "is_printing_alternate_chord",
            "use_known_chord_filter",
        ]
        widgets = {
            "is_lefty": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_printing_alternate_chord": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "use_known_chord_filter": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply bootstrap classes to non-checkbox fields
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({"class": "form-control"})

        # Prefill known_chords_text from JSONField
        if self.instance and self.instance.known_chords:
            self.fields["known_chords_text"].initial = ", ".join(self.instance.known_chords)

    def clean_known_chords_text(self):
        text = self.cleaned_data.get("known_chords_text", "")
        # Split by comma, strip whitespace, ignore empty strings
        return [c.strip() for c in text.split(",") if c.strip()]

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Save known_chords JSONField from text input
        instance.known_chords = self.cleaned_data.get("known_chords_text", [])
        if commit:
            instance.save()
        return instance
