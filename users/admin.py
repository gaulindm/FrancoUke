from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserPreference

# Inline for preferences
class UserPreferenceInline(admin.StackedInline):
    model = UserPreference
    can_delete = False
    verbose_name_plural = 'User Preferences'
    fk_name = 'user'
    fields = (
        'primary_instrument',
        'secondary_instrument',
        'is_lefty',
        'is_printing_alternate_chord',
        'known_chords',  # 👈 add this
        'use_known_chord_filter',  # 👈 New toggle

    )

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = (UserPreferenceInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser','last_login')
    search_fields = ('username', 'email', 'first_name', 'last_name')

# Optional: Clean up this if Profile is unused
# admin.site.unregister(Profile)  # If previously registered
# or just don't import it at all
