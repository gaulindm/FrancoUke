# training/urls.py
from django.urls import path
from . import views

app_name = 'training'

urlpatterns = [
    # Hub - must be first
    path('', views.training_hub, name='hub'),
    
    # Stats personnelles
    path('stats/personal/', views.personal_stats, name='personal_stats'),
    
    # Practice from F2L cases - specific pattern before generic ones
    path('practice-f2l/<slug:slug>/', views.trainer_from_f2l, name='trainer_from_f2l'),
    
    # Entraînement sur un algorithme spécifique
    path('practice/<slug:slug>/', views.algorithm_trainer, name='trainer'),
    
    # Leaderboard pour un algorithme
    path('leaderboard/<slug:slug>/', views.leaderboard, name='leaderboard'),
    
    # API pour sauvegarder un temps (AJAX)
    path('api/<slug:slug>/save/', views.save_training_time, name='save_time'),

    #Moderation des temps du training hub
    path('moderation/', views.leader_moderation_dashboard, name='leader_moderation'),
    path('delete-session/<int:session_id>/', views.delete_training_session, name='delete_session'),
    path('bulk-delete-sessions/', views.bulk_delete_sessions, name='bulk_delete_sessions'),
    path('cuber-stats/<str:cuber_id>/', views.cuber_detailed_stats, name='cuber_stats'),

]