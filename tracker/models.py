from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Activity(models.Model):
    user = models.ForeignKey(User, related_name='activities', on_delete=models.CASCADE, null=True, blank=True)
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)
    name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=50, default='telegram')

    class Meta:
        verbose_name_plural = "Activities"

    @property
    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

class Goal(models.Model):
    PERIOD_CHOICES = [
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
    ]
    user = models.ForeignKey(User, related_name='goals', on_delete=models.CASCADE, null=True, blank=True)
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    target_hours = models.FloatField()
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.target_hours}h/{self.period})"

class KeyValuePair(models.Model):
    user = models.ForeignKey(User, related_name='kv_pairs', on_delete=models.CASCADE, null=True, blank=True)
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)
    key = models.CharField(max_length=255)
    value = models.TextField()

    class Meta:
        unique_together = ('telegram_chat_id', 'key')

    def __str__(self):
        return f"{self.key}: {self.value}"
