# training/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .models import Algorithm, TrainingSession, UserProgress

def training_hub(request):
    """Main training page showing all available algorithms"""
    algorithms = Algorithm.objects.all().order_by('difficulty', 'name')
    
    context = {
        'algorithms': algorithms,
    }
    return render(request, 'training/index.html', context)

def algorithm_trainer(request, slug):
    """Individual algorithm training page"""
    algorithm = get_object_or_404(Algorithm, slug=slug)
    
    # Stats will be None for now (no authentication)
    stats = None
    recent_times = []
    
    context = {
        'algorithm': algorithm,
        'stats': stats,
        'recent_times': recent_times,
    }
    return render(request, 'training/trainer.html', context)

@require_http_methods(["POST"])
def save_training_time(request, slug):
    """API endpoint to save a training time"""
    algorithm = get_object_or_404(Algorithm, slug=slug)
    
    try:
        data = json.loads(request.body)
        time_ms = int(data.get('time_ms'))
        
        # Create training session (anonymous for now)
        session = TrainingSession.objects.create(
            user=None,  # Anonymous
            algorithm=algorithm,
            time_ms=time_ms
        )
        
        return JsonResponse({
            'success': True,
            'is_new_pb': False,  # Can't track PB without auth
            'time_ms': time_ms,
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def leaderboard(request, slug):
    """Leaderboard for a specific algorithm - simplified without auth"""
    algorithm = get_object_or_404(Algorithm, slug=slug)
    
    # Get all recent times (since we don't have user auth)
    recent_times = TrainingSession.objects.filter(
        algorithm=algorithm
    ).order_by('time_ms')[:20]
    
    context = {
        'algorithm': algorithm,
        'recent_times': recent_times,
    }
    return render(request, 'training/leaderboard.html', context)