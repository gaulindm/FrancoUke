# training/views.py - Version complète et corrigée

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Min, Avg, Count, Q
import json

from cube.models import CubeState
from .models import (
    Algorithm, 
    TrainingSession, 
    CuberProgress, 
    LeaderProgress,
    get_user_progress,
    get_recent_times
)
from cubing_users.models import Leader, Cuber, Group, GroupMembership


# ============================================================================
# VUES PRINCIPALES
# ============================================================================

def training_hub(request):
    """Main training page showing all available algorithms"""
    algorithms = Algorithm.objects.all().order_by('difficulty', 'name')
    
    # Détecter le type d'utilisateur
    cuber_id = request.session.get('cuber_id')
    is_leader = False
    is_cuber = False
    
    # Vérifier si c'est un Leader
    if request.user.is_authenticated:
        try:
            leader = Leader.objects.get(user=request.user)
            is_leader = True
        except Leader.DoesNotExist:
            leader = None
    
    # Annoter avec les stats de l'utilisateur si connecté
    if cuber_id:
        # Récupérer tous les progrès du Cuber
        try:
            cuber = Cuber.objects.get(cuber_id=cuber_id)
            is_cuber = True
            
            user_progress = {
                p.algorithm_id: p 
                for p in CuberProgress.objects.filter(cuber=cuber)
            }
            
            for algo in algorithms:
                algo.user_stats = user_progress.get(algo.id)
        except Cuber.DoesNotExist:
            # Cuber ID invalide, nettoyer la session
            del request.session['cuber_id']
    
    elif is_leader:
        # Récupérer tous les progrès du Leader
        user_progress = {
            p.algorithm_id: p 
            for p in LeaderProgress.objects.filter(leader=leader)
        }
        
        for algo in algorithms:
            algo.user_stats = user_progress.get(algo.id)
    
    context = {
        'algorithms': algorithms,
        'is_cuber': is_cuber,
        'is_leader': is_leader,
    }
    return render(request, 'training/index.html', context)


def trainer_from_f2l(request, slug):
    """
    Training view that accepts F2L case slugs (like 'f2l-01')
    Creates or finds a matching Algorithm and redirects to trainer
    """
    # Get the F2L case
    cube_state = get_object_or_404(CubeState, slug=slug, method='cfop')
    
    # Validate that the cube_state has an algorithm
    if not cube_state.algorithm or cube_state.algorithm.strip() == '':
        # Redirect back with error message
        return_url = request.GET.get('return_url', '/methods/cfop/f2l/')
        return redirect(return_url)
    
    # Map difficulty from CubeState to Algorithm difficulty choices
    difficulty_map = {
        'facile': 'apprenti',
        'moyen': 'confirme',
        'difficile': 'speedcube',
    }
    
    algo_difficulty = difficulty_map.get(
        cube_state.difficulty, 
        'confirme'  # default
    )
    
    # Try to find or create a matching Algorithm
    algorithm, created = Algorithm.objects.get_or_create(
        notation=cube_state.algorithm.strip(),
        defaults={
            'name': cube_state.name,
            'slug': f'practice-{slug}',
            'repetitions': 6,
            'difficulty': algo_difficulty,
            'description': cube_state.description or f'Pratique du cas {cube_state.name}',
            'category': 'f2l'
        }
    )
    
    # Get return URL
    return_url = request.GET.get('return_url', '')
    
    # Redirect to the trainer with the algorithm and return URL
    redirect_url = f"/training/practice/{algorithm.slug}/"
    if return_url:
        from urllib.parse import urlencode
        redirect_url += f"?{urlencode({'return_url': return_url})}"
    
    return redirect(redirect_url)


def algorithm_trainer(request, slug):
    """Individual algorithm training page"""
    algorithm = get_object_or_404(Algorithm, slug=slug)
    
    # Récupérer les progrès de l'utilisateur
    stats, is_cuber, is_leader = get_user_progress(request, algorithm)
    
    # Récupérer les derniers temps
    recent_times = get_recent_times(request, algorithm, limit=10)
    
    # Si pas de temps personnels, montrer les derniers temps globaux
    if not recent_times.exists():
        recent_times = TrainingSession.objects.filter(
            algorithm=algorithm
        ).order_by('-created_at')[:5]
    
    context = {
        'algorithm': algorithm,
        'stats': stats,
        'recent_times': recent_times,
        'is_cuber': is_cuber,
        'is_leader': is_leader,
    }
    return render(request, 'training/trainer.html', context)


@require_http_methods(["POST"])
def save_training_time(request, slug):
    """API endpoint to save a training time"""
    algorithm = get_object_or_404(Algorithm, slug=slug)
    
    try:
        data = json.loads(request.body)
        time_ms = int(data.get('time_ms'))
        
        # Déterminer le type d'utilisateur
        cuber_id = request.session.get('cuber_id')
        cuber = None
        leader = None
        session_key = None
        
        # 1. Est-ce un Cuber?
        if cuber_id:
            try:
                cuber = Cuber.objects.get(cuber_id=cuber_id)
            except Cuber.DoesNotExist:
                pass
        
        # 2. Est-ce un Leader?
        if not cuber and request.user.is_authenticated:
            try:
                leader = Leader.objects.get(user=request.user)
            except Leader.DoesNotExist:
                pass
        
        # 3. Sinon, utilisateur anonyme
        if not cuber and not leader:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
        
        # Créer la session de training
        session = TrainingSession.objects.create(
            cuber=cuber,
            leader=leader,
            session_key=session_key,
            algorithm=algorithm,
            time_ms=time_ms
        )
        
        is_new_pb = False
        
        # Mettre à jour les progrès si connecté
        if cuber:
            progress, created = CuberProgress.objects.get_or_create(
                cuber=cuber,
                algorithm=algorithm,
                defaults={
                    'best_time_ms': time_ms,
                    'total_attempts': 1
                }
            )
            
            if not created:
                if time_ms < progress.best_time_ms:
                    is_new_pb = True
                    progress.best_time_ms = time_ms
                progress.total_attempts += 1
                progress.save()
            else:
                is_new_pb = True
        
        elif leader:
            progress, created = LeaderProgress.objects.get_or_create(
                leader=leader,
                algorithm=algorithm,
                defaults={
                    'best_time_ms': time_ms,
                    'total_attempts': 1
                }
            )
            
            if not created:
                if time_ms < progress.best_time_ms:
                    is_new_pb = True
                    progress.best_time_ms = time_ms
                progress.total_attempts += 1
                progress.save()
            else:
                is_new_pb = True
        
        return JsonResponse({
            'success': True,
            'is_new_pb': is_new_pb,
            'time_ms': time_ms,
            'time_formatted': session.time_formatted,
            'user_type': 'cuber' if cuber else ('leader' if leader else 'anonymous')
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def leaderboard(request, slug):
    """Leaderboard for a specific algorithm"""
    algorithm = get_object_or_404(Algorithm, slug=slug)
    
    # Top 50 meilleurs temps (toutes tentatives)
    top_times = TrainingSession.objects.filter(
        algorithm=algorithm
    ).select_related('cuber', 'leader', 'leader__user').order_by('time_ms')[:50]
    
    # Top 50 meilleurs Cubers (records personnels)
    top_cubers = CuberProgress.objects.filter(
        algorithm=algorithm
    ).select_related('cuber').order_by('best_time_ms')[:25]
    
    # Top 25 meilleurs Leaders (records personnels)
    top_leaders = LeaderProgress.objects.filter(
        algorithm=algorithm
    ).select_related('leader', 'leader__user').order_by('best_time_ms')[:25]
    
    # Stats globales
    world_record = top_times.first() if top_times else None
    total_attempts = TrainingSession.objects.filter(algorithm=algorithm).count()
    
    # Moyenne du top 10
    avg_top_10 = None
    if top_times.count() >= 10:
        top_10_times = [t.time_ms for t in top_times[:10]]
        avg_ms = sum(top_10_times) // len(top_10_times)
        
        total_seconds = avg_ms // 1000
        milliseconds = (avg_ms % 1000) // 10
        seconds = total_seconds % 60
        minutes = total_seconds // 60
        avg_top_10 = f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
    
    # Stats personnelles
    user_best = None
    user_rank = None
    is_cuber = False
    is_leader = False
    
    cuber_id = request.session.get('cuber_id')
    if cuber_id:
        is_cuber = True
        try:
            cuber = Cuber.objects.get(cuber_id=cuber_id)
            user_best = CuberProgress.objects.filter(
                cuber=cuber,
                algorithm=algorithm
            ).first()
            
            if user_best:
                better_count = CuberProgress.objects.filter(
                    algorithm=algorithm,
                    best_time_ms__lt=user_best.best_time_ms
                ).count()
                user_rank = better_count + 1
        except:
            pass
    
    elif request.user.is_authenticated:
        try:
            leader = Leader.objects.get(user=request.user)
            is_leader = True
            user_best = LeaderProgress.objects.filter(
                leader=leader,
                algorithm=algorithm
            ).first()
            
            if user_best:
                better_count = LeaderProgress.objects.filter(
                    algorithm=algorithm,
                    best_time_ms__lt=user_best.best_time_ms
                ).count()
                user_rank = better_count + 1
        except:
            pass
    
    context = {
        'algorithm': algorithm,
        'top_times': top_times,
        'top_cubers': top_cubers,
        'top_leaders': top_leaders,
        'world_record': world_record,
        'avg_top_10': avg_top_10,
        'total_attempts': total_attempts,
        'user_best': user_best,
        'user_rank': user_rank,
        'is_cuber': is_cuber,
        'is_leader': is_leader,
    }
    return render(request, 'training/leaderboard.html', context)


def personal_stats(request):
    """Vue des statistiques personnelles"""
    # Cuber
    cuber_id = request.session.get('cuber_id')
    if cuber_id:
        try:
            cuber = Cuber.objects.get(cuber_id=cuber_id)
            progress_list = CuberProgress.objects.filter(
                cuber=cuber
            ).select_related('algorithm').order_by('best_time_ms')
            
            user_display = str(cuber)
            user_type = 'cuber'
        except:
            return redirect('training:hub')
    
    # Leader
    elif request.user.is_authenticated:
        try:
            leader = Leader.objects.get(user=request.user)
            progress_list = LeaderProgress.objects.filter(
                leader=leader
            ).select_related('algorithm').order_by('best_time_ms')
            
            user_display = leader.user.get_full_name() or leader.user.username
            user_type = 'leader'
        except:
            return redirect('training:hub')
    
    else:
        return redirect('training:hub')
    
    # Stats globales
    total_algorithms = progress_list.count()
    total_attempts = sum(p.total_attempts for p in progress_list)
    
    # Meilleurs temps
    best_times = progress_list[:5]
    
    # Algorithmes récemment pratiqués
    recent = progress_list.order_by('-last_practiced')[:5]
    
    context = {
        'progress_list': progress_list,
        'total_algorithms': total_algorithms,
        'total_attempts': total_attempts,
        'best_times': best_times,
        'recent': recent,
        'user_display': user_display,
        'user_type': user_type,
    }
    return render(request, 'training/personal_stats.html', context)


# ============================================================================
# VUES DE MODÉRATION LEADER
# ============================================================================

@login_required
def leader_moderation_dashboard(request):
    """Dashboard pour que les Leaders voient et modèrent les temps de leurs Cubers"""
    # Vérifier que l'utilisateur est un Leader
    try:
        leader = Leader.objects.get(user=request.user)
    except Leader.DoesNotExist:
        messages.error(request, "Vous devez être un Leader pour accéder à cette page.")
        return redirect('training:hub')
    
    # Récupérer tous les Cubers des groupes de ce Leader
    leader_groups = leader.groups.all()
    cuber_ids = GroupMembership.objects.filter(
        group__in=leader_groups,
        status='active'
    ).values_list('cuber_id', flat=True)
    
    cubers = Cuber.objects.filter(cuber_id__in=cuber_ids)
    
    # Filtre par algorithme (optionnel)
    algorithm_filter = request.GET.get('algorithm')
    selected_algorithm = None
    
    if algorithm_filter:
        selected_algorithm = get_object_or_404(Algorithm, slug=algorithm_filter)
    
    # Filtre par Cuber (optionnel)
    cuber_filter = request.GET.get('cuber')
    selected_cuber = None
    
    if cuber_filter:
        try:
            selected_cuber = Cuber.objects.get(
                cuber_id=cuber_filter,
                cuber_id__in=cuber_ids
            )
        except Cuber.DoesNotExist:
            pass
    
    # Récupérer les sessions
    suspicious_sessions = TrainingSession.objects.filter(
        cuber__in=cubers
    ).select_related('cuber', 'algorithm').order_by('-created_at')
    
    if selected_algorithm:
        suspicious_sessions = suspicious_sessions.filter(algorithm=selected_algorithm)
    
    if selected_cuber:
        suspicious_sessions = suspicious_sessions.filter(cuber=selected_cuber)
    
    # Marquer les sessions suspectes
    for session in suspicious_sessions:
        if session.time_ms < 1000:
            session.is_suspicious = True
            session.suspicious_reason = "Temps irréaliste (< 1 seconde)"
        else:
            cuber_avg = TrainingSession.objects.filter(
                cuber=session.cuber,
                algorithm=session.algorithm
            ).exclude(id=session.id).aggregate(Avg('time_ms'))
            
            if cuber_avg['time_ms__avg']:
                avg_time = cuber_avg['time_ms__avg']
                if session.time_ms < (avg_time * 0.5):
                    session.is_suspicious = True
                    session.suspicious_reason = f"50% plus rapide que la moyenne ({avg_time/1000:.2f}s)"
                else:
                    session.is_suspicious = False
            else:
                session.is_suspicious = False
    
    # Filtrer seulement les sessions suspectes si demandé
    show_all = request.GET.get('show_all', 'false') == 'true'
    if not show_all:
        suspicious_sessions = [s for s in suspicious_sessions if getattr(s, 'is_suspicious', False)]
    
    # Stats générales
    total_cubers = cubers.count()
    total_sessions = TrainingSession.objects.filter(cuber__in=cubers).count()
    suspicious_count = sum(1 for s in suspicious_sessions if getattr(s, 'is_suspicious', False))
    
    # Liste des algorithmes pour le filtre
    algorithms = Algorithm.objects.all().order_by('name')
    
    context = {
        'leader': leader,
        'cubers': cubers,
        'suspicious_sessions': suspicious_sessions[:100],
        'total_cubers': total_cubers,
        'total_sessions': total_sessions,
        'suspicious_count': suspicious_count,
        'algorithms': algorithms,
        'selected_algorithm': selected_algorithm,
        'selected_cuber': selected_cuber,
        'show_all': show_all,
    }
    
    return render(request, 'training/leader_moderation.html', context)


@login_required
@require_http_methods(["POST"])
def delete_training_session(request, session_id):
    """Permet à un Leader de supprimer un temps suspect"""
    try:
        leader = Leader.objects.get(user=request.user)
    except Leader.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    session = get_object_or_404(TrainingSession, id=session_id)
    
    if not session.cuber:
        return JsonResponse({'success': False, 'error': 'No cuber associated'}, status=403)
    
    # Vérifier que le Cuber appartient à un groupe du Leader
    leader_groups = leader.groups.all()
    cuber_in_leader_groups = GroupMembership.objects.filter(
        cuber=session.cuber,
        group__in=leader_groups,
        status='active'
    ).exists()
    
    if not cuber_in_leader_groups:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    cuber = session.cuber
    algorithm = session.algorithm
    session.delete()
    
    # Recalculer le meilleur temps
    try:
        progress = CuberProgress.objects.get(cuber=cuber, algorithm=algorithm)
        
        new_best = TrainingSession.objects.filter(
            cuber=cuber,
            algorithm=algorithm
        ).aggregate(Min('time_ms'))
        
        if new_best['time_ms__min']:
            progress.best_time_ms = new_best['time_ms__min']
            progress.total_attempts = TrainingSession.objects.filter(
                cuber=cuber,
                algorithm=algorithm
            ).count()
            progress.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Temps supprimé avec succès.',
                'new_best_time': progress.best_time_formatted,
                'new_total_attempts': progress.total_attempts
            })
        else:
            progress.delete()
            return JsonResponse({
                'success': True,
                'message': 'Temps supprimé. Aucun autre temps pour cet algorithme.',
                'progress_deleted': True
            })
    
    except CuberProgress.DoesNotExist:
        return JsonResponse({'success': True, 'message': 'Temps supprimé.'})


@login_required
@require_http_methods(["POST"])
def bulk_delete_sessions(request):
    """Permet à un Leader de supprimer plusieurs temps en une fois"""
    try:
        leader = Leader.objects.get(user=request.user)
    except Leader.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        session_ids = data.get('session_ids', [])
        
        if not session_ids:
            return JsonResponse({'success': False, 'error': 'No sessions selected'}, status=400)
        
        leader_groups = leader.groups.all()
        authorized_cuber_ids = GroupMembership.objects.filter(
            group__in=leader_groups,
            status='active'
        ).values_list('cuber_id', flat=True)
        
        sessions = TrainingSession.objects.filter(
            id__in=session_ids,
            cuber__cuber_id__in=authorized_cuber_ids
        ).select_related('cuber', 'algorithm')
        
        deleted_count = 0
        affected_progress = set()
        
        for session in sessions:
            affected_progress.add((session.cuber, session.algorithm))
            session.delete()
            deleted_count += 1
        
        # Recalculer les progrès
        for cuber, algorithm in affected_progress:
            try:
                progress = CuberProgress.objects.get(cuber=cuber, algorithm=algorithm)
                
                new_best = TrainingSession.objects.filter(
                    cuber=cuber,
                    algorithm=algorithm
                ).aggregate(Min('time_ms'))
                
                if new_best['time_ms__min']:
                    progress.best_time_ms = new_best['time_ms__min']
                    progress.total_attempts = TrainingSession.objects.filter(
                        cuber=cuber,
                        algorithm=algorithm
                    ).count()
                    progress.save()
                else:
                    progress.delete()
            except CuberProgress.DoesNotExist:
                pass
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} temps supprimés avec succès.',
            'deleted_count': deleted_count
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def cuber_detailed_stats(request, cuber_id):
    """Vue détaillée des stats d'un Cuber spécifique"""
    try:
        leader = Leader.objects.get(user=request.user)
    except Leader.DoesNotExist:
        messages.error(request, "Vous devez être un Leader pour accéder à cette page.")
        return redirect('training:hub')
    
    leader_groups = leader.groups.all()
    
    try:
        cuber = Cuber.objects.get(cuber_id=cuber_id)
        
        is_authorized = GroupMembership.objects.filter(
            cuber=cuber,
            group__in=leader_groups,
            status='active'
        ).exists()
        
        if not is_authorized:
            messages.error(request, "Ce Cuber n'appartient pas à vos groupes.")
            return redirect('training:leader_moderation')
    
    except Cuber.DoesNotExist:
        messages.error(request, "Cuber introuvable.")
        return redirect('training:leader_moderation')
    
    total_sessions = TrainingSession.objects.filter(cuber=cuber).count()
    total_algorithms = CuberProgress.objects.filter(cuber=cuber).count()
    
    all_sessions = TrainingSession.objects.filter(
        cuber=cuber
    ).select_related('algorithm').order_by('-created_at')
    
    progress_list = CuberProgress.objects.filter(
        cuber=cuber
    ).select_related('algorithm').order_by('best_time_ms')
    
    suspicious_sessions = []
    for session in all_sessions[:50]:
        if session.time_ms < 1000:
            session.is_suspicious = True
            session.suspicious_reason = "< 1 seconde"
            suspicious_sessions.append(session)
    
    context = {
        'cuber': cuber,
        'leader': leader,
        'total_sessions': total_sessions,
        'total_algorithms': total_algorithms,
        'all_sessions': all_sessions[:50],
        'progress_list': progress_list,
        'suspicious_sessions': suspicious_sessions,
    }
    
    return render(request, 'training/cuber_detail.html', context)