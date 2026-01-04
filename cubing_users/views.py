# cubing_users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from .models import Cuber, Leader, Group, GroupMembership
from .forms import (
    CuberRegistrationForm, CuberLoginForm,
    LeaderRegistrationForm, LeaderLoginForm,
    GroupCreationForm, JoinGroupForm
)
from .decorators import cuber_required, leader_required
from .authentication import CuberAuthenticationBackend
from .constants import COLOR_EMOJIS



# ==========================================
# VIEWS CUBEURS (Étudiants)
# ==========================================

def cuber_register(request):
    """Inscription d'un nouveau cubeur"""
    if request.method == 'POST':
        form = CuberRegistrationForm(request.POST)
        if form.is_valid():
            cuber = form.save()
            
            # Connecte automatiquement le cubeur
            request.session['cuber_id'] = str(cuber.cuber_id)
            
            messages.success(
                request,
                f"Bienvenue {cuber.color} {cuber.adjective} {cuber.superhero}! 🎉"
            )
            
            # Redirige vers la page pour rejoindre un groupe (optionnel)
            return redirect('cubing_users:join_group')
    else:
        form = CuberRegistrationForm()
    
    return render(request, 'cubing_users/cuber_register.html', {
        'form': form,
    })


def cuber_login(request):
    """Connexion d'un cubeur existant"""
    if request.method == 'POST':
        form = CuberLoginForm(request.POST)
        if form.is_valid():
            color = form.cleaned_data['color']
            adjective = form.cleaned_data['adjective']
            superhero = form.cleaned_data['superhero']
            color_code = form.get_color_code()
            
            # Utilise le backend custom
            backend = CuberAuthenticationBackend()
            cuber = backend.authenticate(
                request,
                color=color,
                adjective=adjective,
                superhero=superhero,
                color_code=','.join(color_code)
            )
            
            if cuber:
                # Connecte le cubeur via session
                request.session['cuber_id'] = str(cuber.cuber_id)
                
                # Met à jour last_active_date
                cuber.last_active_date = timezone.now()
                cuber.save()
                
                messages.success(
                    request,
                    f"Bon retour {cuber.color} {cuber.adjective} {cuber.superhero}! 🎯"
                )
                return redirect('cubing_users:cuber_dashboard')
            else:
                messages.error(
                    request,
                    "Identité ou code couleur incorrect. Vérifie et réessaie!"
                )
    else:
        form = CuberLoginForm()
    
    return render(request, 'cubing_users/cuber_login.html', {
        'form': form,
    })


@cuber_required
def cuber_logout(request):
    """Déconnexion d'un cubeur"""
    cuber_name = f"{request.cuber.color} {request.cuber.adjective} {request.cuber.superhero}"
    
    # Supprime la session
    if 'cuber_id' in request.session:
        del request.session['cuber_id']
    
    messages.info(request, f"À bientôt {cuber_name}! 👋")
    return redirect('cubing_users:cuber_login')


@cuber_required
def cuber_dashboard(request):
    """Dashboard principal du cubeur"""
    cuber = request.cuber
    
    # Récupère les groupes du cubeur
    memberships = GroupMembership.objects.filter(
        cuber=cuber,
        status='active'
    ).select_related('group')
    
    # Statistiques F2L (à connecter avec ton app cube)
    # TODO: Intégrer avec cube.models quand prêt
    f2l_stats = {
        'cases_completed': 0,
        'total_cases': 41,
        'average_time': 0,
        'recent_practice': []
    }
    
    context = {
        'cuber': cuber,
        'memberships': memberships,
        'f2l_stats': f2l_stats,
    }
    
    return render(request, 'cubing_users/cuber_dashboard.html', context)


@cuber_required
def join_group(request):
    """Rejoindre un groupe avec un code"""
    if request.method == 'POST':
        form = JoinGroupForm(request.POST)
        if form.is_valid():
            group = form.get_group()
            cuber = request.cuber
            
            # Vérifie si déjà membre
            if GroupMembership.objects.filter(cuber=cuber, group=group).exists():
                messages.warning(request, f"Tu es déjà membre de {group.group_name}!")
                return redirect('cubing_users:cuber_dashboard')
            
            # Crée l'adhésion
            GroupMembership.objects.create(
                cuber=cuber,
                group=group,
                status='active'
            )
            
            messages.success(
                request,
                f"Bravo! Tu as rejoint {group.group_name}! 🎉"
            )
            return redirect('cubing_users:cuber_dashboard')
    else:
        form = JoinGroupForm()
    
    return render(request, 'cubing_users/join_group.html', {
        'form': form,
    })


@cuber_required
def my_groups(request):
    """Liste des groupes du cubeur"""
    cuber = request.cuber
    
    memberships = GroupMembership.objects.filter(
        cuber=cuber,
        status='active'
    ).select_related('group').prefetch_related('group__leaders')
    
    return render(request, 'cubing_users/my_groups.html', {
        'memberships': memberships,
    })


@cuber_required
def group_leaderboard(request, group_id):
    """Leaderboard d'un groupe spécifique"""
    group = get_object_or_404(Group, group_id=group_id)
    
    # Vérifie que le cubeur est membre
    if not GroupMembership.objects.filter(cuber=request.cuber, group=group).exists():
        messages.error(request, "Tu n'es pas membre de ce groupe!")
        return redirect('cubing_users:cuber_dashboard')
    
    # Récupère tous les membres
    members = GroupMembership.objects.filter(
        group=group,
        status='active'
    ).select_related('cuber')
    
    # TODO: Ajouter les stats F2L réelles quand intégré avec cube app
    leaderboard_data = []
    for membership in members:
        leaderboard_data.append({
            'cuber': membership.cuber,
            'joined_date': membership.joined_date,
            'avg_time': 0,  # À calculer avec les vrais temps
            'cases_completed': 0,  # À calculer avec les vrais progrès
        })
    
    context = {
        'group': group,
        'leaderboard_data': leaderboard_data,
        'is_member': True,
    }
    
    return render(request, 'cubing_users/group_leaderboard.html', context)


# ==========================================
# VIEWS LEADERS (Enseignants/Coachs)
# ==========================================

def leader_register(request):
    """Inscription d'un nouveau leader"""
    if request.method == 'POST':
        form = LeaderRegistrationForm(request.POST)
        if form.is_valid():
            leader = form.save()
            
            # Connecte automatiquement le leader
            login(request, leader.user)
            
            messages.success(
                request,
                f"Bienvenue {leader.user.get_full_name()}! Ton compte leader est créé. 🎓"
            )
            return redirect('cubing_users:leader_dashboard')
    else:
        form = LeaderRegistrationForm()
    
    return render(request, 'cubing_users/leader_register.html', {
        'form': form,
    })


def leader_login(request):
    """Connexion d'un leader existant"""
    if request.method == 'POST':
        form = LeaderLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Authentifie avec email comme username
            user = authenticate(request, username=email, password=password)
            
            if user and hasattr(user, 'leader_profile'):
                login(request, user)
                messages.success(request, f"Bon retour {user.get_full_name()}!")
                return redirect('cubing_users:leader_dashboard')
            else:
                messages.error(
                    request,
                    "Adresse courriel ou mot de passe incorrect."
                )
    else:
        form = LeaderLoginForm()
    
    return render(request, 'cubing_users/leader_login.html', {
        'form': form,
    })


@login_required
@leader_required
def leader_logout(request):
    """Déconnexion d'un leader"""
    logout(request)
    messages.info(request, "Déconnexion réussie. À bientôt!")
    return redirect('cubing_users:leader_login')


@login_required
@leader_required
def leader_dashboard(request):
    """Dashboard principal du leader"""
    leader = request.user.leader_profile
    
    # Récupère tous les groupes du leader
    groups = Group.objects.filter(
        leaders=leader
    ).annotate(
        member_count=Count('groupmembership', filter=Q(groupmembership__status='active'))
    ).order_by('-created_date')
    
    # Stats globales
    total_students = GroupMembership.objects.filter(
        group__leaders=leader,
        status='active'
    ).values('cuber').distinct().count()
    
    context = {
        'leader': leader,
        'groups': groups,
        'total_students': total_students,
    }
    
    return render(request, 'cubing_users/leader_dashboard.html', context)


@login_required
@leader_required
def create_group(request):
    """Créer un nouveau groupe"""
    if request.method == 'POST':
        form = GroupCreationForm(request.POST)
        if form.is_valid():
            group = form.save()
            
            # Ajoute le leader au groupe
            leader = request.user.leader_profile
            group.leaders.add(leader)
            
            messages.success(
                request,
                f"Groupe '{group.group_name}' créé avec succès! Code: {group.group_code}"
            )
            return redirect('cubing_users:group_detail', group_id=group.group_id)
    else:
        form = GroupCreationForm()
    
    return render(request, 'cubing_users/create_group.html', {
        'form': form,
    })


@login_required
@leader_required
def group_detail(request, group_id):
    """Détails d'un groupe (pour le leader)"""
    group = get_object_or_404(Group, group_id=group_id)
    leader = request.user.leader_profile
    
    # Vérifie que le leader a accès à ce groupe
    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')
    
    # Récupère tous les membres
    memberships = GroupMembership.objects.filter(
        group=group,
        status='active'
    ).select_related('cuber').order_by('joined_date')
    
    # Stats du groupe
    stats = {
        'total_members': memberships.count(),
        'active_this_week': memberships.filter(
            cuber__last_active_date__gte=timezone.now() - timedelta(days=7)
        ).count(),
        # TODO: Ajouter stats F2L réelles
    }
    
    context = {
        'group': group,
        'memberships': memberships,
        'stats': stats,
    }
    
    return render(request, 'cubing_users/group_detail.html', context)


@login_required
@leader_required
def group_roster(request, group_id):
    """Liste complète des membres d'un groupe"""
    group = get_object_or_404(Group, group_id=group_id)
    leader = request.user.leader_profile
    
    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')
    
    memberships = GroupMembership.objects.filter(
        group=group,
        status='active'
    ).select_related('cuber').order_by('cuber__color', 'cuber__adjective')
    
    return render(request, 'cubing_users/group_roster.html', {
        'group': group,
        'memberships': memberships,
    })


@login_required
@leader_required
def student_progress(request, group_id, cuber_id):
    """Détails du progrès d'un étudiant spécifique"""
    group = get_object_or_404(Group, group_id=group_id)
    cuber = get_object_or_404(Cuber, cuber_id=cuber_id)
    leader = request.user.leader_profile
    
    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')
    
    # Vérifie que le cuber est dans le groupe
    membership = get_object_or_404(
        GroupMembership,
        cuber=cuber,
        group=group,
        status='active'
    )
    
    # TODO: Récupérer les vraies stats F2L depuis l'app cube
    progress_data = {
        'cases_completed': 0,
        'total_cases': 41,
        'average_time': 0,
        'recent_sessions': [],
        'best_times': [],
    }
    
    context = {
        'group': group,
        'cuber': cuber,
        'membership': membership,
        'progress_data': progress_data,
    }
    
    return render(request, 'cubing_users/student_progress.html', context)


@login_required
@leader_required
def group_statistics(request, group_id):
    """Statistiques globales du groupe"""
    group = get_object_or_404(Group, group_id=group_id)
    leader = request.user.leader_profile
    
    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')
    
    memberships = GroupMembership.objects.filter(
        group=group,
        status='active'
    ).select_related('cuber')
    
    # Stats agrégées
    stats = {
        'total_members': memberships.count(),
        'active_today': memberships.filter(
            cuber__last_active_date__date=timezone.now().date()
        ).count(),
        'active_this_week': memberships.filter(
            cuber__last_active_date__gte=timezone.now() - timedelta(days=7)
        ).count(),
        'active_this_month': memberships.filter(
            cuber__last_active_date__gte=timezone.now() - timedelta(days=30)
        ).count(),
        # TODO: Ajouter stats F2L réelles
        'avg_completion': 0,
        'avg_time': 0,
    }
    
    context = {
        'group': group,
        'stats': stats,
        'memberships': memberships,
    }
    
    return render(request, 'cubing_users/group_statistics.html', context)


@login_required
@leader_required
def print_login_cards(request, group_id):
    """Page pour imprimer les cartes de connexion des membres"""
    group = get_object_or_404(Group, group_id=group_id)
    leader = request.user.leader_profile
    
    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')
    
    memberships = GroupMembership.objects.filter(
        group=group,
        status='active'
    ).select_related('cuber')
    
    # Note: Les color_codes sont hashés, donc on ne peut pas les afficher
    # Le leader devra les noter au moment de la création des comptes
    
    context = {
        'group': group,
        'memberships': memberships,
        'color_emojis': COLOR_EMOJIS,
    }
    
    return render(request, 'cubing_users/print_login_cards.html', context)


# ==========================================
# VIEWS PUBLIQUES
# ==========================================

def home(request):
    """Page d'accueil du système cubing"""
    context = {
        'total_cubers': Cuber.objects.count(),
        'total_groups': Group.objects.count(),
    }
    return render(request, 'cubing_users/home.html', context)