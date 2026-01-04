# cubing_users/urls.py
from django.urls import path
from . import views

app_name = 'cubing_users'

urlpatterns = [
    # ==========================================
    # URLs Publiques
    # ==========================================
    path('', views.home, name='home'),
    
    # ==========================================
    # URLs Cubeurs (Étudiants)
    # ==========================================
    path('cuber/register/', views.cuber_register, name='cuber_register'),
    path('cuber/login/', views.cuber_login, name='cuber_login'),
    path('cuber/logout/', views.cuber_logout, name='cuber_logout'),
    path('cuber/dashboard/', views.cuber_dashboard, name='cuber_dashboard'),
    path('cuber/join-group/', views.join_group, name='join_group'),
    path('cuber/my-groups/', views.my_groups, name='my_groups'),
    path('cuber/group/<uuid:group_id>/leaderboard/', views.group_leaderboard, name='group_leaderboard'),
    
    # ==========================================
    # URLs Leaders (Enseignants/Coachs)
    # ==========================================
    path('leader/register/', views.leader_register, name='leader_register'),
    path('leader/login/', views.leader_login, name='leader_login'),
    path('leader/logout/', views.leader_logout, name='leader_logout'),
    path('leader/dashboard/', views.leader_dashboard, name='leader_dashboard'),
    
    # Gestion des groupes
    path('leader/group/create/', views.create_group, name='create_group'),
    path('leader/group/<uuid:group_id>/', views.group_detail, name='group_detail'),
    path('leader/group/<uuid:group_id>/roster/', views.group_roster, name='group_roster'),
    path('leader/group/<uuid:group_id>/statistics/', views.group_statistics, name='group_statistics'),
    path('leader/group/<uuid:group_id>/print-cards/', views.print_login_cards, name='print_login_cards'),
    
    # Suivi des étudiants
    path('leader/group/<uuid:group_id>/student/<uuid:cuber_id>/', views.student_progress, name='student_progress'),
]