from django import forms
from .models import PerformanceAvailability

class PerformanceAvailabilityForm(forms.ModelForm):
    class Meta:
        model = PerformanceAvailability
        fields = ["status"]
        widgets = {
            "status": forms.RadioSelect
        }
