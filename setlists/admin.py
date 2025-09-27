from django.contrib import admin
from .models import SetList, SetListSong


class SetListSongInline(admin.TabularInline):
    model = SetListSong
    extra = 1
    ordering = ["order"]
    autocomplete_fields = ["song"]  # helpful if you have 800+ songs
    fields = ["song", "order", "scroll_speed"]


@admin.register(SetList)
class SetListAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    inlines = [SetListSongInline]


@admin.register(SetListSong)
class SetListSongAdmin(admin.ModelAdmin):
    list_display = ("setlist", "song", "order", "scroll_speed")
    list_filter = ("setlist",)
    ordering = ["setlist", "order"]
    search_fields = ("song__songTitle", "setlist__name")
