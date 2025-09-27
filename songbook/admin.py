from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html
from django.db.models import Value
from django.db.models.functions import Concat
from django import forms

from .models import Song, SongFormatting
from .utils.admin_chordpro_transposer import transpose_chordpro_text
from .utils.transposer import transpose_chordpro  # ✅ Using your transposer.py


# ---------- SongFormatting Admin ----------

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
    list_display = ('user', 'song', 'display_intro_font_size', 'display_verse_font_size', 'display_chorus_font_size')

    def display_intro_font_size(self, obj):
        return obj.intro.get("font_size", "Default") if obj.intro else "Default"
    display_intro_font_size.short_description = "Intro Font Size"

    def display_verse_font_size(self, obj):
        return obj.verse.get("font_size", "Default") if obj.verse else "Default"
    display_verse_font_size.short_description = "Verse Font Size"

    def display_chorus_font_size(self, obj):
        return obj.chorus.get("font_size", "Default") if obj.chorus else "Default"
    display_chorus_font_size.short_description = "Chorus Font Size"


# ---------- Song Admin ----------

@admin.action(description="Transpose songChordPro UP 1 semitone")
def transpose_up_1(modeladmin, request, queryset):
    for song in queryset:
        if not song.songChordPro:
            continue
        song.songChordPro = transpose_chordpro_text(song.songChordPro, 1)
        song.save()
    messages.success(request, f"{queryset.count()} song(s) transposed UP 1 semitone.")


@admin.action(description="Transpose songChordPro DOWN 1 semitone")
def transpose_down_1(modeladmin, request, queryset):
    for song in queryset:
        if not song.songChordPro:
            continue
        song.songChordPro = transpose_chordpro_text(song.songChordPro, -1)
        song.save()
    messages.success(request, f"{queryset.count()} song(s) transposed DOWN 1 semitone.")


# ✅ Custom filter to include Hidden (None)
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
        elif value:
            return queryset.filter(site_name=value)
        return queryset

@admin.action(description="Hide selected songs (set site_name=None)")
def mark_hidden(modeladmin, request, queryset):
    updated = queryset.update(site_name=None)
    messages.success(request, f"{updated} song(s) marked as hidden.")


@admin.action(description="Restore hidden songs to FrancoUke")
def restore_francouke(modeladmin, request, queryset):
    updated = queryset.filter(site_name__isnull=True).update(site_name='FrancoUke')
    messages.success(request, f"{updated} hidden song(s) restored to FrancoUke.")


@admin.action(description="Restore hidden songs to StrumSphere")
def restore_strumsphere(modeladmin, request, queryset):
    updated = queryset.filter(site_name__isnull=True).update(site_name='StrumSphere')
    messages.success(request, f"{updated} hidden song(s) restored to StrumSphere.")

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    change_form_template = "admin/song_change_form_with_transpose.html"

    list_display = ['songTitle', 'get_artist', 'date_posted', 'get_year', 'get_youtube', 'site_name', 'get_tags']
    list_editable = ['site_name']
    search_fields = ['songTitle', 'metadata__artist']
    ordering = ('metadata__artist',)
    list_filter = [SiteNameFilter]  # ✅ Custom filter
    actions = [
        transpose_up_1,
        transpose_down_1,
        mark_hidden,             # ✅ Hide songs
        restore_francouke,       # ✅ Restore to FrancoUke
        restore_strumsphere,     # ✅ Restore to StrumSphere
    ]



    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            tags_string=Concat('tags__name', Value(', '))
        )

    def get_year(self, obj):
        return obj.metadata.get('year', 'Unknown') if obj.metadata else 'No Metadata'
    get_year.admin_order_field = 'metadata__year'
    get_year.short_description = 'Year'

    def get_youtube(self, obj):
        youtube_url = obj.metadata.get('youtube', '') if obj.metadata else ''
        return format_html('<a href="{}" target="_blank">{}</a>', youtube_url, youtube_url) if youtube_url else 'No Metadata'
    get_youtube.short_description = 'YouTube'

    def get_artist(self, obj):
        return obj.metadata.get('artist', 'Unknown') if obj.metadata else ''
    get_artist.short_description = 'Artist'


    def get_view_on_site_url(self, obj):
        if obj is None or obj.pk is None:
            return None
        return reverse("songbook:score_view", kwargs={"pk": obj.pk})


    def get_tags(self, obj):
        return ", ".join(obj.tags.names())
    get_tags.admin_order_field = 'tags_string'
    get_tags.short_description = 'Tags'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:song_id>/transpose/<semitones>/",
                self.admin_site.admin_view(self.transpose_song),
                name="songbook_song_transpose",
            ),
        ]
        return custom_urls + urls

    def transpose_song(self, request, song_id, semitones):
        try:
            semitones = int(semitones)
        except ValueError:
            messages.error(request, "Invalid semitone value.")
            return redirect(f"../../")

        song = get_object_or_404(Song, pk=song_id)
        if not song.songChordPro:
            messages.warning(request, "This song has no songChordPro text.")
            return redirect(f"../../")

        original = song.songChordPro
        song.songChordPro = transpose_chordpro(original, semitones)
        song.save()
        direction = "up" if semitones > 0 else "down"
        messages.success(request, f"Transposed {direction} {abs(semitones)} semitone(s).")
        return redirect(f"../../")

