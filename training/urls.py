# training/urls.py
from django.urls import path
from . import views

app_name = 'training'

urlpatterns = [
    path('', views.training_hub, name='hub'),
    path('<slug:slug>/', views.algorithm_trainer, name='trainer'),
    path('<slug:slug>/save/', views.save_training_time, name='save_time'),
    path('<slug:slug>/leaderboard/', views.leaderboard, name='leaderboard'),
]