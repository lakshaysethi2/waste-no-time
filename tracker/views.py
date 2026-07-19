from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from .models import Activity, Goal, KeyValuePair
from .trajectory import get_trajectory
from django.utils import timezone
from datetime import timedelta
import json

from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

@require_GET
def api_activities(request):
    chat_id = request.GET.get('chat_id')
    if not chat_id:
        return JsonResponse({'error': 'chat_id required'}, status=400)
    
    activities = Activity.objects.filter(telegram_chat_id=chat_id).order_by('-end_time')[:50]
    data = [{
        'id': a.id,
        'name': a.name,
        'start_time': a.start_time.isoformat(),
        'end_time': a.end_time.isoformat() if a.end_time else None,
        'duration_seconds': a.duration.total_seconds() if a.duration else 0,
        'notes': a.notes,
        'source': a.source
    } for a in activities]
    return JsonResponse(data, safe=False)

@require_GET
def api_trajectory(request):
    chat_id = request.GET.get('chat_id')
    category = request.GET.get('category')
    period = request.GET.get('period', 'month')
    
    if not chat_id or not category:
        return JsonResponse({'error': 'chat_id and category required'}, status=400)
    
    data = get_trajectory(chat_id, category, period)
    return JsonResponse(data)

@require_GET
def api_dashboard(request):
    chat_id = request.GET.get('chat_id')
    if not chat_id:
        return JsonResponse({'error': 'chat_id required'}, status=400)
    
    # Get all active categories for this user
    categories = Activity.objects.filter(telegram_chat_id=chat_id).values_list('name', flat=True).distinct()
    
    trajectories = []
    for cat in categories:
        trajectories.append(get_trajectory(chat_id, cat, 'month'))
        
    return JsonResponse({
        'trajectories': trajectories,
        'chat_id': chat_id,
        'server_time': timezone.now().isoformat()
    })
