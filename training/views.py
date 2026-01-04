# training/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Min, Avg, Count, Q
import json

from .models import (
    Algorithm, 
    TrainingSession, 
    CuberProgress, 
    LeaderProgress,
    get_user_progress,
    get_recent_times
)


def training_hub(request):
    """Main training page showing all available algorithms"""
    algorithms = Algorithm.objects.all().order_by('difficulty', 'name')
    
    # Détecter le type d'utilisateur
    cuber_id = request.session.get('cuber_id')
    is_leader = False
    
    if request.user.is_authenticated:
        try:
            from cubing_users.models import Leader
            leader = Leader.objects.get(user=request.user)
            is_leader = True
        except:
            pass
    
    # Annoter avec les stats de l'utilisateur si connecté
    if cuber_id:
        # Récupérer tous les progrès du Cuber
        from cubing_users.models import Cuber
        try:
            cuber = Cuber.objects.get(cuber_id=cuber_id)
            user_progress = {
                p.algorithm_id: p 
                for p in CuberProgress.objects.filter(cuber=cuber)
            }
            
            for algo in algorithms:
                algo.user_stats = user_progress.get(algo.id)
        except:
            pass
    
    elif is_leader:
        # Récupérer tous les progrès du Leader
        from cubing_users.models import Leader
        try:
            leader = Leader.objects.get(user=request.user)
            user_progress = {
                p.algorithm_id: p 
                for p in LeaderProgress.objects.filter(leader=leader)
            }
            
            for algo in algorithms:
                algo.user_stats = user_progress.get(algo.id)
        except:
            pass
    
    context = {
        'algorithms': algorithms,
        'is_cuber': bool(cuber_id),
        'is_leader': is_leader,
    }
    return render(request, 'training/index.html', context)


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
            from cubing_users.models import Cuber
            try:
                cuber = Cuber.objects.get(cuber_id=cuber_id)
            except Cuber.DoesNotExist:
                pass
        
        # 2. Est-ce un Leader?
        if not cuber and request.user.is_authenticated:
            from cubing_users.models import Leader
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
        from cubing_users.models import Cuber
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
        from cubing_users.models import Leader
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
        from cubing_users.models import Cuber
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
        from cubing_users.models import Leader
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