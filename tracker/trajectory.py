from datetime import timedelta
from django.utils import timezone
import math
from .models import Activity, Goal

def get_trajectory(chat_id, category_name, period='month'):
    now = timezone.now()
    
    # 1. Actual hours logged so far in current period
    if period == 'month':
        start_of_period = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # End of month
        if now.month == 12:
            end_of_period = now.replace(year=now.year + 1, month=1, day=1) - timedelta(seconds=1)
        else:
            end_of_period = now.replace(month=now.month + 1, day=1) - timedelta(seconds=1)
    elif period == 'week':
        start_of_period = now - timedelta(days=now.weekday())
        start_of_period = start_of_period.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_period = start_of_period + timedelta(days=7) - timedelta(seconds=1)
    else: # day
        start_of_period = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_period = start_of_period + timedelta(days=1) - timedelta(seconds=1)

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
    recent_days = 28
    daily_paces = []
    for i in range(1, recent_days + 1):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_activities = Activity.objects.filter(
            telegram_chat_id=chat_id,
            name=category_name,
            start_time__gte=day_start,
            end_time__lte=day_end
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
        
    # 3. Days remaining
    days_remaining = (end_of_period - now).total_seconds() / (24 * 3600)
    if days_remaining < 0: days_remaining = 0
    
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
