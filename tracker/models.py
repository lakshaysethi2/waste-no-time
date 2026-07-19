from django.db import models

class Activity(models.Model):
    user_id = models.BigIntegerField(default=1040271347, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    notes = models.TextField(blank=True, default='')
    source = models.CharField(max_length=50, default='telegram')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user_id', 'start_time', 'end_time']),
        ]

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

class Goal(models.Model):
    PERIOD_CHOICES = [
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
    ]
    GOAL_TYPE_CHOICES = [
        ('at_least', 'At Least'),
        ('at_most', 'At Most'),
        ('range', 'Range'),
    ]
    user_id = models.BigIntegerField(default=1040271347, db_index=True)
    category_name = models.CharField(max_length=255, db_index=True)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='day')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES, default='at_least')
    target_min_seconds = models.IntegerField(default=0)
    target_max_seconds = models.IntegerField(default=0)
    priority = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'category_name', 'period')

    def __str__(self):
        return f"{self.category_name} ({self.period}: {self.goal_type})"

class KeyValuePair(models.Model):
    user_id = models.BigIntegerField(default=1040271347, db_index=True)
    key = models.CharField(max_length=255, db_index=True)
    value = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('user_id', 'key')

    def __str__(self):
        return f"{self.key}={self.value}"
