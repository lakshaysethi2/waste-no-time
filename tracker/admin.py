from django.contrib import admin
from .models import Activity, Goal, KeyValuePair

admin.site.register(Activity)
admin.site.register(Goal)
admin.site.register(KeyValuePair)
