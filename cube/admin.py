from django.contrib import admin
from django import forms
from .models import CubeState
from .widgets import CubeStateWidget


class CubeStateAdminForm(forms.ModelForm):
    class Meta:
        model = CubeState
        fields = '__all__'
        widgets = {
            "json_state": CubeStateWidget(),
            "json_highlight": forms.HiddenInput(),
        }


@admin.register(CubeState)
class CubeStateAdmin(admin.ModelAdmin):
    form = CubeStateAdminForm

    list_display = (
        "name",
        "method",
        "hand_orientation",   # 👈 added
        "step_number",
        "roofpig_colored",
    )

    list_filter = (
        "method",
        "hand_orientation",   # 👈 added
    )

    search_fields = ("name", "description", "algorithm")
    ordering = ("method", "step_number")
    actions = ['duplicate_cube_states']

    def duplicate_cube_states(self, request, queryset):
        """Duplicate selected cube states"""
        count = 0
        for cube_state in queryset:
            cube_state.pk = None
            cube_state.slug = ''
            cube_state.name = f"{cube_state.name} (Copy)"
            cube_state.save()
            count += 1

        self.message_user(
            request,
            f"Successfully duplicated {count} cube state(s)."
        )

    duplicate_cube_states.short_description = "Duplicate selected cube states"
