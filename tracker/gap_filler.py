from datetime import timedelta
from django.utils import timezone
from .models import Activity

def create_activity_with_gap_filling(user_id, tag, notes="", now=None):
    if now is None:
        now = timezone.now()
    
    # Find most recent activity for user
    latest_activity = Activity.objects.filter(user_id=user_id).order_by('-end_time').first()
    
    # 760 minutes lookback limit
    lookback_limit = now - timedelta(minutes=760)
    
    if latest_activity and latest_activity.end_time >= lookback_limit:
        start_time = latest_activity.end_time
    else:
        # Cold start bootstrap: 1 minute prior to now
        start_time = now - timedelta(minutes=1)
        
    if start_time >= now:
        start_time = now - timedelta(seconds=1)
        
    end_time = now
    
    activity = Activity.objects.create(
        user_id=user_id,
        name=tag.strip(),
        start_time=start_time,
        end_time=end_time,
        notes=notes.strip(),
        source='telegram'
    )
    return activity

def get_time_spent_today_seconds(user_id, tag):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    activities = Activity.objects.filter(
        user_id=user_id,
        name__iexact=tag.strip(),
        end_time__gte=today_start
    )
    total_seconds = 0
    for act in activities:
        st = max(act.start_time, today_start)
        et = act.end_time
        duration = (et - st).total_seconds()
        if duration > 0:
            total_seconds += duration
    return total_seconds

def format_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
