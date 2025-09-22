from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import UserPreference

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


class UserPreferenceForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = UserPreference
        fields = ["primary_instrument", "secondary_instrument", "is_lefty", "is_printing_alternate_chord"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_classes()

    def clean(self):
        cleaned_data = super().clean()
        primary = cleaned_data.get("primary_instrument")
        secondary = cleaned_data.get("secondary_instrument")

        if primary and secondary and primary == secondary:
            self.add_error("secondary_instrument", "Primary and Secondary instruments must be different.")
        return cleaned_data
