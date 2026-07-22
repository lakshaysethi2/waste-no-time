import functools
import hashlib
import hmac
import json

from django.conf import settings
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Activity
from .trajectory import get_trajectory


def index(request):
    return render(request, 'index.html')


def _session_chat_id(request):
    """Return the authenticated Telegram user ID held in this browser session."""
    return request.session.get('telegram_chat_id')


def _require_telegram_session(view):
    @functools.wraps(view)
    def wrapped(request, *args, **kwargs):
        if _session_chat_id(request) is None:
            return JsonResponse({'error': 'authentication required'}, status=401)
        return view(request, *args, **kwargs)

    return wrapped


def _valid_telegram_login(payload):
    """Verify Telegram Login Widget data as specified by Telegram's auth protocol."""
    supplied_hash = payload.get('hash')
    if not supplied_hash or not settings.TELEGRAM_BOT_API_KEY:
        return False

    fields = {key: value for key, value in payload.items() if key != 'hash'}
    if not fields.get('id') or not fields.get('auth_date'):
        return False

    try:
        age_seconds = timezone.now().timestamp() - int(fields['auth_date'])
        if age_seconds < 0 or age_seconds > settings.TELEGRAM_AUTH_MAX_AGE_SECONDS:
            return False
    except (TypeError, ValueError):
        return False

    check_string = '\n'.join(f'{key}={value}' for key, value in sorted(fields.items()))
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_API_KEY.encode()).digest()
    expected_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_hash, supplied_hash)


@csrf_exempt
@require_POST
def api_telegram_login(request):
    """Create a session only after server-side Telegram Login Widget validation."""
    try:
        payload = json.loads(request.body)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'invalid JSON payload'}, status=400)

    if not isinstance(payload, dict) or not _valid_telegram_login(payload):
        return JsonResponse({'error': 'invalid Telegram authentication'}, status=403)

    request.session.cycle_key()
    request.session['telegram_chat_id'] = int(payload['id'])
    return JsonResponse({'chat_id': int(payload['id'])})


@csrf_exempt
@require_POST
def api_logout(request):
    logout(request)
    return JsonResponse({'ok': True})


@require_GET
@_require_telegram_session
def api_activities(request):
    activities = Activity.objects.filter(telegram_chat_id=_session_chat_id(request)).order_by('-end_time')[:50]
    data = [{
        'id': activity.id,
        # Camel-case fields retain the dashboard's established client contract.
        'displayName': activity.name,
        'startTime': activity.start_time.isoformat(),
        'endTime': activity.end_time.isoformat() if activity.end_time else None,
        'durationSeconds': activity.duration.total_seconds() if activity.duration else 0,
        'notes': activity.notes,
        'source': activity.source,
    } for activity in activities]
    return JsonResponse({'activities': data})


@require_GET
@_require_telegram_session
def api_trajectory(request):
    category = request.GET.get('category')
    period = request.GET.get('period', 'month')
    if not category:
        return JsonResponse({'error': 'category required'}, status=400)
    if period not in {'day', 'week', 'month'}:
        return JsonResponse({'error': 'period must be day, week, or month'}, status=400)
    return JsonResponse(get_trajectory(_session_chat_id(request), category, period))


@require_GET
@_require_telegram_session
def api_dashboard(request):
    chat_id = _session_chat_id(request)
    categories = Activity.objects.filter(telegram_chat_id=chat_id).values_list('name', flat=True).distinct()
    return JsonResponse({
        'trajectories': [get_trajectory(chat_id, category, 'month') for category in categories],
        'server_time': timezone.now().isoformat(),
    })
