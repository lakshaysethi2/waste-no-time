from django.utils import timezone
from datetime import timedelta
from .models import Activity

def log_activity_gap_filled(telegram_chat_id, tag, notes=None, source='telegram'):
    now = timezone.now()
    lookback_limit = now - timedelta(minutes=760)

    # Find the most recent activity for this user
    last_activity = Activity.objects.filter(
        telegram_chat_id=telegram_chat_id,
        end_time__isnull=False
    ).order_by('-end_time').first()

    if last_activity:
        # Merge: if same name and recent enough (< 10 min gap), extend the last activity
        if last_activity.name == tag and (now - last_activity.end_time) < timedelta(minutes=10):
            last_activity.end_time = now
            last_activity.save()
            return last_activity

        if last_activity.end_time >= lookback_limit:
            start_time = last_activity.end_time
        else:
            # If the last activity was too long ago, start 1 minute ago
            start_time = now - timedelta(minutes=1)
    else:
        # Cold start: first activity ever
        start_time = now - timedelta(minutes=1)

    # If by any chance start_time is in the future compared to now (shouldn't happen)
    if start_time > now:
        start_time = now - timedelta(minutes=1)

    activity = Activity.objects.create(
        telegram_chat_id=telegram_chat_id,
        name=tag,
        start_time=start_time,
        end_time=now,
        notes=notes,
        source=source
    )
    return activity
