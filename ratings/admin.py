from django.contrib import admin

from .models import SongRating


@admin.register(SongRating)
class SongRatingAdmin(admin.ModelAdmin):
    """Lets you read, edit or delete any rating or comment (moderation)."""
    list_display = ("song", "user", "stars", "playability", "singability", "updated")
    list_filter = ("stars", "playability", "singability")
    search_fields = ("song__songTitle", "user__username", "comment")
    raw_id_fields = ("song", "user")  # avoids a dropdown with every song in it
