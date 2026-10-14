from django.contrib import admin
from django.db.models import Count
from .models import SetList, SetListSong, SongSuggestion, SongSuggester
from django.db import transaction


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
    actions = ["duplicate_setlists"]

    @admin.action(description="Duplicate selected setlists (no event link)")
    def duplicate_setlists(self, request, queryset):
        count = 0
        for original in queryset:
            with transaction.atomic():
                songs = list(original.songs.all())
                copy = SetList.objects.create(
                    name=f"{original.name} (Copy)",
                    group=original.group,
                    created_by=request.user,
                )
                SetListSong.objects.bulk_create([
                    SetListSong(setlist=copy, song=s.song, order=s.order)
                    for s in songs
                ])
            count += 1
        self.message_user(
            request,
            f"Duplicated {count} setlist(s). Open the copy to link it to an event.",
        )

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