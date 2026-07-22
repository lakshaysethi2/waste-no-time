from datetime import timedelta
from django.utils import timezone
import math

import pytz

from .models import Activity, Goal, KeyValuePair


def _get_user_tz(chat_id):
    """Return the user's configured timezone as a pytz tzinfo, defaulting to UTC."""
    try:
        tz_name = KeyValuePair.objects.get(telegram_chat_id=chat_id, key="tz").value
    except KeyValuePair.DoesNotExist:
        return pytz.UTC
    except Exception:
        return pytz.UTC
    try:
        return pytz.timezone(tz_name)
    except Exception:
        return pytz.UTC


def _normalize(tz, dt):
    """Normalize a replaced datetime for pytz to handle DST transitions."""
    try:
        # dt is already aware in tz; normalize re-computes offset
        return tz.normalize(dt)
    except Exception:
        return dt


def get_trajectory(chat_id, category_name, period='month'):
    now_utc = timezone.now()
    user_tz = _get_user_tz(chat_id)
    now_local = now_utc.astimezone(user_tz)

    # 1. Actual hours logged so far in current period — boundaries in user's TZ, converted to UTC for DB
    if period == 'month':
        start_local = _normalize(user_tz, now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0))
        if start_local.month == 12:
            next_month_local = _normalize(user_tz, start_local.replace(year=start_local.year + 1, month=1, day=1))
        else:
            next_month_local = _normalize(user_tz, start_local.replace(month=start_local.month + 1, day=1))
        end_local = next_month_local - timedelta(seconds=1)
    elif period == 'week':
        # Monday as start of week in user's local calendar
        start_local = _normalize(
            user_tz,
            (now_local - timedelta(days=now_local.weekday())).replace(hour=0, minute=0, second=0, microsecond=0),
        )
        end_local = start_local + timedelta(days=7) - timedelta(seconds=1)
    else:  # day
        start_local = _normalize(user_tz, now_local.replace(hour=0, minute=0, second=0, microsecond=0))
        end_local = start_local + timedelta(days=1) - timedelta(seconds=1)

    start_of_period = start_local.astimezone(pytz.UTC)
    end_of_period = end_local.astimezone(pytz.UTC)

    actual_activities = Activity.objects.filter(
        telegram_chat_id=chat_id,
        name=category_name,
        start_time__gte=start_of_period,
        end_time__lte=end_of_period
    )
    
    actual_so_far = timedelta()
    for act in actual_activities:
        if act.duration:
            actual_so_far += act.duration
            
    # 2. Recent daily pace (exponential recency-weighted average)
    # Half-life: 7 days. Weight = 0.5^(days_ago / 7)
    # Buckets are calculated in the user's local calendar day, then converted to UTC for DB queries.
    recent_days = 28
    daily_paces = []
    for i in range(1, recent_days + 1):
        day_start_local = _normalize(
            user_tz,
            (now_local - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0),
        )
        day_end_local = day_start_local + timedelta(days=1)
        day_start_utc = day_start_local.astimezone(pytz.UTC)
        day_end_utc = day_end_local.astimezone(pytz.UTC)

        day_activities = Activity.objects.filter(
            telegram_chat_id=chat_id,
            name=category_name,
            start_time__gte=day_start_utc,
            end_time__lte=day_end_utc
        )
        day_total = timedelta()
        for act in day_activities:
            if act.duration:
                day_total += act.duration

        weight = 0.5 ** ((i - 1) / 7)
        daily_paces.append((day_total.total_seconds(), weight))

    total_weight = sum(w for p, w in daily_paces)
    if total_weight > 0:
        weighted_avg_pace_seconds = sum(p * w for p, w in daily_paces) / total_weight
    else:
        weighted_avg_pace_seconds = 0

    # 3. Days remaining (from user's local now to end of local period)
    days_remaining = (end_local - now_local).total_seconds() / (24 * 3600)
    if days_remaining < 0:
        days_remaining = 0
    
    # 4. Forecasted Period Total
    forecast_remaining = weighted_avg_pace_seconds * days_remaining
    forecast_total_seconds = actual_so_far.total_seconds() + forecast_remaining
    
    # 5. Goal Comparison
    goal = Goal.objects.filter(telegram_chat_id=chat_id, category=category_name, period=period).first()
    goal_target_seconds = (goal.target_hours * 3600) if goal else 0
    
    forecast_gap_seconds = forecast_total_seconds - goal_target_seconds
    
    # Required daily pace to meet goal
    if days_remaining > 0:
        required_pace_seconds = max(0, (goal_target_seconds - actual_so_far.total_seconds()) / days_remaining)
    else:
        required_pace_seconds = 0
        
    return {
        'category': category_name,
        'actual_so_far_hours': actual_so_far.total_seconds() / 3600,
        'forecast_total_hours': forecast_total_seconds / 3600,
        'goal_target_hours': goal_target_seconds / 3600,
        'forecast_gap_hours': forecast_gap_seconds / 3600,
        'required_daily_pace_hours': required_pace_seconds / 3600,
        'recent_pace_hours': weighted_avg_pace_seconds / 3600,
        'status': 'On Path' if forecast_gap_seconds >= 0 else 'Correction Needed'
    }
