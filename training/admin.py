# training/admin.py
from django.contrib import admin
from django.db.models import Count, Min, Avg
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Algorithm, TrainingSession, UserProgress

@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    list_display = ['name', 'notation', 'difficulty_badge', 'repetitions', 'category', 'total_sessions', 'slug']
    list_filter = ['difficulty', 'category']
    search_fields = ['name', 'notation', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'slug', 'notation', 'repetitions')
        }),
        ('Classification', {
            'fields': ('difficulty', 'category')
        }),
        ('Description', {
            'fields': ('description',)
        }),
    )
    
    def difficulty_badge(self, obj):
        colors = {
            'apprenti': 'success',
            'confirme': 'warning',
            'speedcube': 'danger',
            'maitre': 'primary'
        }
        color = colors.get(obj.difficulty, 'secondary')
        return format_html(
            '<span style="background-color: #{}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            {
                'success': '28a745',
                'warning': 'ffc107',
                'danger': 'dc3545',
                'primary': '007bff',
                'secondary': '6c757d'
            }[color],
            obj.get_difficulty_display()
        )
    difficulty_badge.short_description = 'Niveau'
    
    def total_sessions(self, obj):
        count = TrainingSession.objects.filter(algorithm=obj).count()
        return format_html(
            '<strong>{}</strong> sessions',
            count
        )
    total_sessions.short_description = 'Sessions totales'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(session_count=Count('trainingsession'))


# training/admin.py

@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['user_link', 'algorithm', 'time_formatted_colored', 'created_at', 'is_personal_best']
    list_filter = ['algorithm', 'created_at', 'user']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'algorithm__name']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'time_display', 'is_personal_best']
    
    fieldsets = (
        ('Session', {
            'fields': ('user', 'algorithm', 'time_ms', 'time_display')
        }),
        ('Informations', {
            'fields': ('created_at', 'is_personal_best')
        }),
    )
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return 'Anonyme'
    user_link.short_description = 'Utilisateur'
    user_link.admin_order_field = 'user__username'
    
    def time_display(self, obj):
        """Affichage formaté du temps dans l'admin"""
        if obj.time_ms is None:
            return '-'
        return obj.time_formatted
    time_display.short_description = 'Temps formaté'
    
    def time_formatted_colored(self, obj):
        if obj.time_ms is None:
            return '-'
        
        time_str = obj.time_formatted
        # Colorer selon la vitesse (ajuste selon tes besoins)
        if obj.time_ms < 5000:  # Moins de 5 secondes
            color = 'green'
        elif obj.time_ms < 10000:  # Moins de 10 secondes
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            time_str
        )
    time_formatted_colored.short_description = 'Temps'
    time_formatted_colored.admin_order_field = 'time_ms'
    
    def is_personal_best(self, obj):
        if not obj.user or obj.time_ms is None:
            return '-'
        
        try:
            progress = UserProgress.objects.get(user=obj.user, algorithm=obj.algorithm)
            is_pb = obj.time_ms == progress.best_time_ms
            if is_pb:
                return format_html(
                    '<span style="color: gold; font-size: 20px;">🏆</span>'
                )
            return '❌'
        except UserProgress.DoesNotExist:
            return '-'
    is_personal_best.short_description = 'Record'

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user_link', 'algorithm', 'best_time_badge', 'total_attempts', 'last_practiced', 'view_sessions']
    list_filter = ['algorithm', 'last_practiced', 'algorithm__difficulty']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'algorithm__name']
    readonly_fields = ['last_practiced', 'best_time_formatted', 'average_time', 'improvement_rate']
    date_hierarchy = 'last_practiced'
    
    fieldsets = (
        ('Utilisateur et Algorithme', {
            'fields': ('user', 'algorithm')
        }),
        ('Statistiques', {
            'fields': ('best_time_ms', 'best_time_formatted', 'total_attempts', 'average_time', 'improvement_rate', 'last_practiced')
        }),
    )
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.username)
    user_link.short_description = 'Utilisateur'
    user_link.admin_order_field = 'user__username'
    
    def best_time_badge(self, obj):
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold;">{}</span>',
            obj.best_time_formatted
        )
    best_time_badge.short_description = 'Meilleur temps'
    best_time_badge.admin_order_field = 'best_time_ms'
    
    def average_time(self, obj):
        sessions = TrainingSession.objects.filter(
            user=obj.user,
            algorithm=obj.algorithm
        )[:10]  # Dernières 10 sessions
        
        if sessions:
            avg = sum(s.time_ms for s in sessions) / len(sessions)
            total_seconds = int(avg // 1000)
            milliseconds = int((avg % 1000) // 10)
            seconds = total_seconds % 60
            minutes = total_seconds // 60
            return f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
        return '-'
    average_time.short_description = 'Moyenne (10 dernières)'
    
    def improvement_rate(self, obj):
        sessions = TrainingSession.objects.filter(
            user=obj.user,
            algorithm=obj.algorithm
        ).order_by('created_at')
        
        if sessions.count() < 2:
            return '-'
        
        first_time = sessions.first().time_ms
        improvement = ((first_time - obj.best_time_ms) / first_time) * 100
        
        if improvement > 0:
            return format_html(
                '<span style="color: green;">📈 +{:.1f}%</span>',
                improvement
            )
        elif improvement < 0:
            return format_html(
                '<span style="color: red;">📉 {:.1f}%</span>',
                improvement
            )
        return '='
    improvement_rate.short_description = 'Amélioration'
    
    def view_sessions(self, obj):
        url = reverse('admin:training_trainingsession_changelist')
        return format_html(
            '<a href="{}?user__id__exact={}&algorithm__id__exact={}" class="button">Voir les sessions</a>',
            url,
            obj.user.id,
            obj.algorithm.id
        )
    view_sessions.short_description = 'Sessions'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'algorithm')


# Actions personnalisées
@admin.action(description='Exporter les données sélectionnées (CSV)')
def export_as_csv(modeladmin, request, queryset):
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="training_sessions.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Utilisateur', 'Algorithme', 'Temps (ms)', 'Date'])
    
    for obj in queryset:
        writer.writerow([
            obj.user.username if obj.user else 'Anonyme',
            obj.algorithm.name,
            obj.time_ms,
            obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

TrainingSessionAdmin.actions = [export_as_csv]

# training/admin.py (ajouter à la fin)

from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Avg, Min

class TrainingAdminSite(admin.AdminSite):
    site_header = "FrancontCube - Administration de l'Entraînement"
    site_title = "FrancontCube Admin"
    index_title = "Tableau de bord de l'entraînement"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='training_dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        # Statistiques globales
        total_sessions = TrainingSession.objects.count()
        total_users = User.objects.filter(trainingsession__isnull=False).distinct().count()
        total_algorithms = Algorithm.objects.count()
        
        # Top performers
        top_performers = UserProgress.objects.select_related('user', 'algorithm').order_by('best_time_ms')[:10]
        
        # Algorithmes les plus pratiqués
        popular_algorithms = Algorithm.objects.annotate(
            session_count=Count('trainingsession')
        ).order_by('-session_count')[:5]
        
        # Activité récente
        recent_sessions = TrainingSession.objects.select_related('user', 'algorithm').order_by('-created_at')[:10]
        
        context = {
            'total_sessions': total_sessions,
            'total_users': total_users,
            'total_algorithms': total_algorithms,
            'top_performers': top_performers,
            'popular_algorithms': popular_algorithms,
            'recent_sessions': recent_sessions,
        }
        
        return render(request, 'admin/training_dashboard.html', context)

# Si tu veux utiliser le site admin personnalisé (optionnel)
# training_admin_site = TrainingAdminSite(name='training_admin')
# training_admin_site.register(Algorithm, AlgorithmAdmin)
# training_admin_site.register(TrainingSession, TrainingSessionAdmin)
# training_admin_site.register(UserProgress, UserProgressAdmin)