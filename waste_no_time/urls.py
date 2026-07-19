from django.contrib import admin
from django.urls import path
from tracker.views import dashboard_view, api_activities_json

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='dashboard'),
    path('api/activities/', api_activities_json, name='api_activities'),
]
