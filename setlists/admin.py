from django.contrib import admin
from django.db.models import Count
from .models import SetList, SetListSong, SongSuggestion, SongSuggester


class SetListSongInline(admin.TabularInline):
    model = SetListSong
    extra = 1
    ordering = ["order"]
    autocomplete_fields = ["song"]  # helpful if you have 800+ songs
    fields = ["song", "order"]


@admin.register(SetList)
class SetListAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "created_at")
    list_filter = ("group",)
    search_fields = ("name",)
    inlines = [SetListSongInline]


@admin.register(SetListSong)
class SetListSongAdmin(admin.ModelAdmin):
    list_display = ("setlist", "order", "song")
    list_filter = ("setlist",)
    ordering = ("setlist", "order")

    def get_fields(self, request, obj=None):
        if obj:  # editing existing entry
            return ("setlist", "song", "order")
        return ("setlist", "song")  # creating new entry


class SongSuggesterInline(admin.TabularInline):
    """Who suggested this song, shown inside the suggestion."""
    model = SongSuggester
    extra = 0
    fields = ["user", "note", "created_at"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["user"]


@admin.register(SongSuggestion)
class SongSuggestionAdmin(admin.ModelAdmin):
    list_display = (
        "song", "group", "status", "suggester_count",
        "reviewed_by", "reviewed_at", "created_at",
    )
    list_filter = ("group", "status")
    search_fields = ("song__songTitle",)
    autocomplete_fields = ["song"]
    raw_id_fields = ["reviewed_by", "added_to_setlist"]
    inlines = [SongSuggesterInline]

    def get_queryset(self, request):
        # Count suggesters in the database query itself, not one query per row
        return super().get_queryset(request).annotate(
            _suggester_count=Count("suggesters")
        )

    @admin.display(description="Suggested by", ordering="_suggester_count")
    def suggester_count(self, obj):
        return obj._suggester_count