# training/urls.py
from django.urls import path
from . import views

app_name = 'training'

urlpatterns = [
    path('', views.training_hub, name='hub'),

    
    # Entraînement sur un algorithme spécifique
    path('<slug:slug>/', views.algorithm_trainer, name='trainer'),
    
    # API pour sauvegarder un temps (AJAX)
    path('api/<slug:slug>/save/', views.save_training_time, name='save_time'),
    
    # Leaderboard pour un algorithme
    path('<slug:slug>/leaderboard/', views.leaderboard, name='leaderboard'),
    
    # Stats personnelles (optionnel - à implémenter)
    path('stats/personal/', views.personal_stats, name='personal_stats'),

    #path('<slug:slug>/', views.algorithm_trainer, name='trainer'),
    #path('<slug:slug>/save/', views.save_training_time, name='save_time'),
    #path('<slug:slug>/leaderboard/', views.leaderboard, name='leaderboard'),
]