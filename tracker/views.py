from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from .models import Activity
from .gap_filler import format_duration

def dashboard_view(request):
    user_id = 1040271347
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    recent_activities = Activity.objects.filter(user_id=user_id)[:20]
    current_activity = recent_activities.first() if recent_activities else None

    acts = Activity.objects.filter(user_id=user_id, end_time__gte=today_start)
    summary = {}
    for act in acts:
        st = max(act.start_time, today_start)
        dur = (act.end_time - st).total_seconds()
        if dur > 0:
            summary[act.name] = summary.get(act.name, 0) + dur

    sorted_summary = sorted(summary.items(), key=lambda x: x[1], reverse=True)
    summary_formatted = [{"name": name, "duration": format_duration(secs), "seconds": secs} for name, secs in sorted_summary]

    context = {
        "current_activity": current_activity,
        "summary": summary_formatted,
        "recent_activities": recent_activities,
    }
    return render(request, "tracker/dashboard.html", context)

def api_activities_json(request):
    user_id = 1040271347
    acts = Activity.objects.filter(user_id=user_id)[:50]
    data = [{
        "name": a.name,
        "start_time": a.start_time.isoformat(),
        "end_time": a.end_time.isoformat(),
        "notes": a.notes
    } for a in acts]
    return JsonResponse({"activities": data})
