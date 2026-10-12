from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html
from django.db.models import Value
from django.db.models.functions import Concat
from django import forms
from django.core.exceptions import PermissionDenied

from .models import Song, SongFormatting
from .utils.admin_chordpro_transposer import transpose_chordpro_text
from .utils.transposer import transpose_chordpro


# ============================================================================
# Helper
# ============================================================================

SONG_TAGGER_GROUP = "Song Taggers"


def is_song_tagger(user):
    """
    Return True if the user belongs to the Song Taggers group.

    Superusers are never treated as taggers, even if they happen
    to belong to the group.
    """
    if user.is_superuser:
        return False

    return user.groups.filter(name=SONG_TAGGER_GROUP).exists()


# ============================================================================
# SongFormatting Admin
# ============================================================================

class SongFormattingAdminForm(forms.ModelForm):
    class Meta:
        model = SongFormatting
        fields = '__all__'
        widgets = {
            'intro': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'verse': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'chorus': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'bridge': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'interlude': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'outro': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
        }


@admin.register(SongFormatting)
class SongFormattingAdmin(admin.ModelAdmin):
    form = SongFormattingAdminForm

    list_display = (
        'user',
        'song',
        'display_intro_font_size',
        'display_verse_font_size',
        'display_chorus_font_size',
    )

    def display_intro_font_size(self, obj):
        return obj.intro.get("font_size", "Default") if obj.intro else "Default"

    display_intro_font_size.short_description = "Intro Font Size"

    def display_verse_font_size(self, obj):
        return obj.verse.get("font_size", "Default") if obj.verse else "Default"

    display_verse_font_size.short_description = "Verse Font Size"

    def display_chorus_font_size(self, obj):
        return obj.chorus.get("font_size", "Default") if obj.chorus else "Default"

    display_chorus_font_size.short_description = "Chorus Font Size"


# ============================================================================
# Song Actions
# ============================================================================

@admin.action(description="🌐 Make selected songs PUBLIC")
def make_public(modeladmin, request, queryset):
    if not request.user.is_superuser:
        raise PermissionDenied

    updated = queryset.update(is_public=True)
    messages.success(
        request,
        f"{updated} song(s) marked as PUBLIC."
    )


# TEMPORARY: bulk-assign origin to NBU for initial data cleanup.
@admin.action(description="🏷️ Assign selected songs to NBU")
def assign_origin_nbu(modeladmin, request, queryset):
    if not request.user.is_superuser:
        raise PermissionDenied

    updated = queryset.update(origin="NBU")
    messages.success(
        request,
        f"{updated} song(s) assigned to NBU."
    )


@admin.action(description="🔒 Make selected songs PRIVATE")
def make_private(modeladmin, request, queryset):
    if not request.user.is_superuser:
        raise PermissionDenied

    updated = queryset.update(is_public=False)
    messages.success(
        request,
        f"{updated} song(s) marked as PRIVATE."
    )


@admin.action(description="Transpose songChordPro UP 1 semitone")
def transpose_up_1(modeladmin, request, queryset):
    if not request.user.is_superuser:
        raise PermissionDenied

    count = 0

    for song in queryset:
        if not song.songChordPro:
            continue

        song.songChordPro = transpose_chordpro_text(
            song.songChordPro,
            1
        )
        song.save()
        count += 1

    messages.success(
        request,
        f"{count} song(s) transposed UP 1 semitone."
    )


@admin.action(description="📋 Duplicate selected songs (as PUBLIC copies)")
def duplicate_songs(modeladmin, request, queryset):
    if not request.user.is_superuser:
        raise PermissionDenied

    duplicated_count = 0

    for song in queryset:
        original_pk = song.pk
        original_tags = list(song.tags.names())

        song.pk = None
        song.id = None
        song._state.adding = True

        song.songTitle = f"{song.songTitle} (Copy)"
        song.is_public = True
        song.cloned_from_id = original_pk

        song.save()

        if original_tags:
            song.tags.set(*original_tags)

        duplicated_count += 1

    messages.success(
        request,
        f"{duplicated_count} song(s) duplicated as PUBLIC copies."
    )


@admin.action(description="Transpose songChordPro DOWN 1 semitone")
def transpose_down_1(modeladmin, request, queryset):
    if not request.user.is_superuser:
        raise PermissionDenied

    count = 0

    for song in queryset:
        if not song.songChordPro:
            continue

        song.songChordPro = transpose_chordpro_text(
            song.songChordPro,
            -1
        )
        song.save()
        count += 1

    messages.success(
        request,
        f"{count} song(s) transposed DOWN 1 semitone."
    )


@admin.action(description="Hide selected songs (set site_name=None)")
def mark_hidden(modeladmin, request, queryset):
    if not request.user.is_superuser:
        raise PermissionDenied

    updated = queryset.update(site_name=None)

    messages.success(
        request,
        f"{updated} song(s) marked as hidden."
    )


@admin.action(description="Restore hidden songs to FrancoUke")
def restore_francouke(modeladmin, request, queryset):
    if not request.user.is_superuser:
        raise PermissionDenied

    updated = queryset.filter(
        site_name__isnull=True
    ).update(
        site_name='FrancoUke'
    )

    messages.success(
        request,
        f"{updated} hidden song(s) restored to FrancoUke."
    )


@admin.action(description="Restore hidden songs to StrumSphere")
def restore_strumsphere(modeladmin, request, queryset):
    if not request.user.is_superuser:
        raise PermissionDenied

    updated = queryset.filter(
        site_name__isnull=True
    ).update(
        site_name='StrumSphere'
    )

    messages.success(
        request,
        f"{updated} hidden song(s) restored to StrumSphere."
    )


# ============================================================================
# Filters
# ============================================================================

class SiteNameFilter(admin.SimpleListFilter):
    title = 'Site Name'
    parameter_name = 'site_name'

    def lookups(self, request, model_admin):
        return [
            ('FrancoUke', 'FrancoUke'),
            ('StrumSphere', 'StrumSphere'),
            ('hidden', 'Hidden (None)'),
        ]

    def queryset(self, request, queryset):
        value = self.value()

        if value == 'hidden':
            return queryset.filter(site_name__isnull=True)

        if value:
            return queryset.filter(site_name=value)

        return queryset


class PrivacyFilter(admin.SimpleListFilter):
    title = 'Privacy Status'
    parameter_name = 'is_public'

    def lookups(self, request, model_admin):
        return [
            ('public', '🌐 Public'),
            ('private', '🔒 Private'),
        ]

    def queryset(self, request, queryset):
        value = self.value()

        if value == 'public':
            return queryset.filter(is_public=True)

        if value == 'private':
            return queryset.filter(is_public=False)

        return queryset


# ============================================================================
# Song Admin
# ============================================================================

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):

    change_form_template = "admin/song_change_form_with_transpose.html"

    # ------------------------------------------------------------------------
    # Normal / Superuser configuration
    # ------------------------------------------------------------------------

    list_display = [
        'songTitle',
        'get_artist',
        'contributor',
        'origin',
        'get_privacy_status',
        'get_is_clone',
        'date_posted',
        'get_year',
        'get_youtube',
        'site_name',
        'get_tags',
    ]

    list_editable = ['site_name']

    search_fields = [
        'songTitle',
        'metadata__artist',
        'contributor__username',
    ]

    ordering = ('metadata__artist',)

    list_filter = [
        SiteNameFilter,
        PrivacyFilter,
        'contributor',
    ]

    actions = [
        make_public,
        make_private,
        duplicate_songs,
        transpose_up_1,
        transpose_down_1,
        mark_hidden,
        restore_francouke,
        restore_strumsphere,
        assign_origin_nbu,
    ]

    fieldsets = (
        (
            'Song Information',
            {
                'fields': (
                    'songTitle',
                    'songChordPro',
                    'contributor',
                    'site_name',
                )
            },
        ),
        (
            'Privacy Settings',
            {
                'fields': (
                    'is_public',
                    'cloned_from',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Metadata',
            {
                'fields': (
                    'metadata',
                    'tags',
                    'revised_on',
                    'acknowledgement',
                    'origin',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            'Advanced',
            {
                'fields': (
                    'lyrics_with_chords',
                    'scroll_speed',
                ),
                'classes': ('collapse',),
            },
        ),
    )

    # ------------------------------------------------------------------------
    # Dynamic configuration for Song Taggers
    # ------------------------------------------------------------------------

    def get_list_display(self, request):
        """
        Song Taggers get a simplified list focused on tagging.
        """

        if is_song_tagger(request.user):
            return [
                'songTitle',
                'get_artist',
                'get_tags',
                'get_year',
                'site_name',
            ]

        return super().get_list_display(request)

    def get_list_display_links(self, request, list_display):
        """
        Make the song title the link for taggers.
        """

        if is_song_tagger(request.user):
            return ('songTitle',)

        return super().get_list_display_links(
            request,
            list_display,
        )

    def get_list_editable(self, request):
        """
        Taggers cannot edit site_name from the list.
        """

        if is_song_tagger(request.user):
            return ()

        return super().get_list_editable(request)

    def get_list_filter(self, request):
        """
        Taggers get a simpler filtering interface.
        """

        if is_song_tagger(request.user):
            return []

        return super().get_list_filter(request)

    def get_search_fields(self, request):
        """
        Taggers can search by title and artist.
        """

        if is_song_tagger(request.user):
            return [
                'songTitle',
                'metadata__artist',
            ]

        return super().get_search_fields(request)

    def get_ordering(self, request):
        """
        Keep the normal ordering for everyone.
        """

        return super().get_ordering(request)

    def get_actions(self, request):
        """
        Song Taggers receive NO bulk actions.

        This is important because several of the existing actions
        modify song content, privacy, origin, or visibility.
        """

        if is_song_tagger(request.user):
            return {}

        return super().get_actions(request)

    def get_fieldsets(self, request, obj=None):
        """
        Song Taggers receive a very small edit form.

        They can see:
            - Song title
            - Artist
            - Tags

        They can edit:
            - Tags ONLY
        """

        if is_song_tagger(request.user):
            return (
                (
                    'Song',
                    {
                        'fields': (
                            'songTitle',
                            'get_artist',
                            'tags',
                        ),
                    },
                ),
            )

        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        """
        For Song Taggers, title and artist are display-only.

        'tags' is deliberately NOT included here, making it
        the only editable field.
        """

        if is_song_tagger(request.user):
            return (
                'songTitle',
                'get_artist',
            )

        return super().get_readonly_fields(request, obj)

    # ------------------------------------------------------------------------
    # Permissions
    # ------------------------------------------------------------------------

    def has_add_permission(self, request):
        """
        Song Taggers cannot create songs.

        Superusers and other appropriately-permissioned users
        retain normal Django behavior.
        """

        if is_song_tagger(request.user):
            return False

        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        """
        Song Taggers cannot delete songs.

        Superusers and other appropriately-permissioned users
        retain normal Django behavior.
        """

        if is_song_tagger(request.user):
            return False

        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        """
        Song Taggers need Django's normal change_song permission.

        The actual editable fields are restricted separately
        by get_fieldsets() and get_readonly_fields().
        """

        return super().has_change_permission(request, obj)

    # ------------------------------------------------------------------------
    # Queryset
    # ------------------------------------------------------------------------

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.annotate(
            tags_string=Concat(
                'tags__name',
                Value(', ')
            )
        ).select_related(
            'contributor',
            'cloned_from',
        )

    # ------------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------------

    def get_privacy_status(self, obj):
        if obj.is_public:
            return format_html(
                '<span style="color: green;">🌐 Public</span>'
            )

        return format_html(
            '<span style="color: orange;">🔒 Private</span>'
        )

    get_privacy_status.short_description = 'Privacy'
    get_privacy_status.admin_order_field = 'is_public'

    def get_is_clone(self, obj):
        if obj.cloned_from:
            return format_html(
                '📋 <a href="{}">{}</a>',
                reverse(
                    'admin:songbook_song_change',
                    args=[obj.cloned_from.pk],
                ),
                obj.cloned_from.songTitle[:30],
            )

        return '-'

    get_is_clone.short_description = 'Cloned From'

    def get_year(self, obj):
        return (
            obj.metadata.get('year', 'Unknown')
            if obj.metadata
            else 'No Metadata'
        )

    get_year.admin_order_field = 'metadata__year'
    get_year.short_description = 'Year'

    def get_youtube(self, obj):
        youtube_url = (
            obj.metadata.get('youtube', '')
            if obj.metadata
            else ''
        )

        if not youtube_url:
            return 'No Metadata'

        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            youtube_url,
            youtube_url,
        )

    get_youtube.short_description = 'YouTube'

    def get_artist(self, obj):
        return (
            obj.metadata.get('artist', 'Unknown')
            if obj.metadata
            else ''
        )

    get_artist.short_description = 'Artist'

    def get_view_on_site_url(self, obj):
        if obj is None or obj.pk is None:
            return None

        return reverse(
            "songbook:chord_sheet",
            kwargs={"pk": obj.pk},
        )

    def get_tags(self, obj):
        return ", ".join(obj.tags.names())

    get_tags.admin_order_field = 'tags_string'
    get_tags.short_description = 'Tags'

    # ------------------------------------------------------------------------
    # Custom URLs
    # ------------------------------------------------------------------------

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "<int:song_id>/transpose/<semitones>/",
                self.admin_site.admin_view(
                    self.transpose_song
                ),
                name="songbook_song_transpose",
            ),
        ]

        return custom_urls + urls

    # ------------------------------------------------------------------------
    # Transpose endpoint
    # ------------------------------------------------------------------------

    def transpose_song(self, request, song_id, semitones):
        """
        Custom transpose endpoint.

        Only superusers are allowed to use this endpoint.

        This check is intentionally present even though the transpose
        controls/actions are hidden from Song Taggers. It prevents a
        tagger from bypassing the UI and manually calling the URL.
        """

        if not request.user.is_superuser:
            raise PermissionDenied

        try:
            semitones = int(semitones)
        except ValueError:
            messages.error(
                request,
                "Invalid semitone value.",
            )
            return redirect("../../")

        song = get_object_or_404(
            Song,
            pk=song_id,
        )

        if not song.songChordPro:
            messages.warning(
                request,
                "This song has no songChordPro text.",
            )
            return redirect("../../")

        original = song.songChordPro

        song.songChordPro = transpose_chordpro(
            original,
            semitones,
        )

        song.save()

        direction = "up" if semitones > 0 else "down"

        messages.success(
            request,
            f"Transposed {direction} "
            f"{abs(semitones)} semitone(s).",
        )

        return redirect("../../")