# assets/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Asset, AssetCollection, AssetCollectionItem, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        'admin_thumbnail_tag',
        'title',
        'type',
        'file_size_display',
        'dimensions_display',
        'uploaded_by',
        'created_at',
        'is_public'
    )
    list_filter = ('type', 'provider', 'is_public', 'created_at', 'tags')
    search_fields = ('title', 'caption', 'alt_text', 'id')
    readonly_fields = (
        'admin_thumbnail_tag',
        'id',
        'mime_type',
        'size',
        'width',
        'height',
        'sha256',
        'created_at',
        'uploaded_at'
    )
    
    fieldsets = (
        ('File/URL', {
            'fields': ('file', 'external_url', 'provider')
        }),
        ('Details', {
            'fields': ('title', 'caption', 'alt_text', 'type', 'is_public')
        }),
        ('Organization', {
            'fields': ('tags', 'uploaded_by')
        }),
        ('Technical Info (Auto-generated)', {
            'fields': (
                'admin_thumbnail_tag',
                'id',
                'mime_type',
                'size',
                'width',
                'height',
                'sha256',
                'created_at',
                'uploaded_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    
    def file_size_display(self, obj):
        if not obj.size:
            return '—'
        size = obj.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    file_size_display.short_description = 'Size'
    
    def dimensions_display(self, obj):
        if obj.width and obj.height:
            return f"{obj.width} × {obj.height}"
        return '—'
    dimensions_display.short_description = 'Dimensions'
    
    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


class AssetCollectionItemInline(admin.TabularInline):
    model = AssetCollectionItem
    extra = 1
    fields = ('asset', 'order', 'caption')
    autocomplete_fields = ['asset']


@admin.register(AssetCollection)
class AssetCollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at', 'asset_count')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')
    list_filter = ('created_at',)
    inlines = [AssetCollectionItemInline]
    date_hierarchy = 'created_at'
    
    def asset_count(self, obj):
        return obj.assets.count()
    asset_count.short_description = 'Assets'