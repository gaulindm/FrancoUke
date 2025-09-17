from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import UserPreference

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['primary_instrument', 'secondary_instrument', 'is_lefty', 'is_printing_alternate_chord']

    def clean(self):
        cleaned_data = super().clean()
        primary = cleaned_data.get("primary_instrument")
        secondary = cleaned_data.get("secondary_instrument")

        if primary and secondary and primary == secondary:
            self.add_error("secondary_instrument", "Primary and Secondary instruments must be different.")
        return cleaned_data
