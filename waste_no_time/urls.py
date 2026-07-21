from django.contrib import admin
from django.urls import path

from tracker import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('api/auth/telegram', views.api_telegram_login, name='api_telegram_login'),
    path('api/auth/logout', views.api_logout, name='api_logout'),
    path('api/activities', views.api_activities, name='api_activities'),
    path('api/trajectory', views.api_trajectory, name='api_trajectory'),
    path('api/dashboard', views.api_dashboard, name='api_dashboard'),
]
