from django.contrib import admin
from .models import Asset

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("title", "file")  # keep it simple
    search_fields = ("title",)
