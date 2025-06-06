from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Value
from django.db.models.functions import Concat
from .models import Song, SongFormatting
from django import forms

# Custom admin form to show JSON fields as editable text areas
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

# Custom display function for JSON fields in admin list view
@admin.register(SongFormatting)
class SongFormattingAdmin(admin.ModelAdmin):
    form = SongFormattingAdminForm
    list_display = ('user', 'song', 'display_intro_font_size', 'display_verse_font_size', 'display_chorus_font_size')

    def display_intro_font_size(self, obj):
        """ Show font size for Intro in admin list view """
        return obj.intro.get("font_size", "Default") if obj.intro else "Default"
    display_intro_font_size.short_description = "Intro Font Size"

    def display_verse_font_size(self, obj):
        """ Show font size for Verse in admin list view """
        return obj.verse.get("font_size", "Default") if obj.verse else "Default"
    display_verse_font_size.short_description = "Verse Font Size"

    def display_chorus_font_size(self, obj):
        """ Show font size for Chorus in admin list view """
        return obj.chorus.get("font_size", "Default") if obj.chorus else "Default"
    display_chorus_font_size.short_description = "Chorus Font Size"

# ✅ Single Admin Panel with Filtering by Site Name
@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['songTitle', 'get_artist', 'date_posted', 'get_year', 'get_youtube', 'site_name', 'get_tags']
    list_editable = ['site_name']
    search_fields = ['songTitle', 'metadata__artist']
    ordering = ('metadata__artist',)
    list_filter = ['site_name']  # ✅ Admin panel filter to separate FrancoUke & StrumSphere

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

    def get_tags(self, obj):
        return ", ".join(obj.tags.names())
    get_tags.admin_order_field = 'tags_string'  # Enable sorting by annotated field
    get_tags.short_description = 'Tags'
