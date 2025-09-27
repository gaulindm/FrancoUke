from django.apps import AppConfig

class SetlistsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "setlists"   # 👈 MUST match the folder name exactly
    verbose_name = "Set Lists"  # optional, for nicer display in admin
