# training/admin.py
from django.contrib import admin
from .models import Algorithm, TrainingSession, CuberProgress, LeaderProgress


@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    list_display = ['name', 'notation', 'difficulty', 'category', 'repetitions']
    list_filter = ['difficulty', 'category']
    search_fields = ['name', 'notation']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['difficulty', 'name']


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['user_type_display', 'user_display_name', 'algorithm', 'time_formatted', 'created_at']
    list_filter = ['algorithm', 'created_at']
    search_fields = ['cuber__color', 'cuber__superhero', 'leader__user__username', 'algorithm__name']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'user_type_display', 'user_display_name']
    
    def user_type_display(self, obj):
        """Affiche le type d'utilisateur"""
        if obj.cuber:
            return "🎨 Cuber"
        elif obj.leader:
            return "👨‍🏫 Leader"
        else:
            return "👤 Anonyme"
    user_type_display.short_description = 'Type'
    
    def user_display_name(self, obj):
        """Affiche le nom de l'utilisateur"""
        return obj.user_display
    user_display_name.short_description = 'Utilisateur'
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user_type_display', 'user_display_name', 'cuber', 'leader', 'session_key')
        }),
        ('Performance', {
            'fields': ('algorithm', 'time_ms', 'time_formatted')
        }),
        ('Métadonnées', {
            'fields': ('created_at',)
        }),
    )


@admin.register(CuberProgress)
class CuberProgressAdmin(admin.ModelAdmin):
    list_display = ['cuber_display', 'algorithm', 'best_time_formatted', 'total_attempts', 'last_practiced']
    list_filter = ['algorithm', 'last_practiced']
    search_fields = ['cuber__color', 'cuber__superhero', 'algorithm__name']
    ordering = ['-last_practiced']
    readonly_fields = ['last_practiced']
    
    def cuber_display(self, obj):
        """Affiche le nom coloré du Cuber"""
        return f"🎨 {obj.cuber}"
    cuber_display.short_description = 'Cuber'


@admin.register(LeaderProgress)
class LeaderProgressAdmin(admin.ModelAdmin):
    list_display = ['leader_display', 'algorithm', 'best_time_formatted', 'total_attempts', 'last_practiced']
    list_filter = ['algorithm', 'last_practiced']
    search_fields = ['leader__user__username', 'leader__user__first_name', 'algorithm__name']
    ordering = ['-last_practiced']
    readonly_fields = ['last_practiced']
    
    def leader_display(self, obj):
        """Affiche le nom du Leader"""
        name = obj.leader.user.get_full_name() or obj.leader.user.username
        return f"👨‍🏫 {name}"
    leader_display.short_description = 'Leader'