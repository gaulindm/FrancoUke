# favorites/admin.py
from django.contrib import admin

from .models import SongFavorite


@admin.register(SongFavorite)
class SongFavoriteAdmin(admin.ModelAdmin):
    list_display = ("song", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("song__songTitle", "user__username")
    raw_id_fields = ("song", "user")      # thousands of songs: avoid a giant dropdown