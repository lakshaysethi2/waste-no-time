from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from tracker.models import Activity
from tracker.gap_filler import log_activity_gap_filled

class GapFillerTest(TestCase):
    def setUp(self):
        self.chat_id = 12345

    def test_cold_start(self):
        # First activity ever should start 1 minute ago
        now = timezone.now()
        activity = log_activity_gap_filled(self.chat_id, "Programming")
        
        self.assertEqual(activity.name, "Programming")
        self.assertAlmostEqual(activity.end_time.timestamp(), now.timestamp(), delta=1)
        self.assertAlmostEqual((activity.end_time - activity.start_time).total_seconds(), 60, delta=1)

    def test_gap_filling(self):
        # Create an initial activity ending 30 minutes ago
        start_time = timezone.now() - timedelta(minutes=60)
        end_time = timezone.now() - timedelta(minutes=30)
        Activity.objects.create(
            telegram_chat_id=self.chat_id,
            name="Sleep",
            start_time=start_time,
            end_time=end_time
        )
        
        # Log new activity now
        now = timezone.now()
        activity = log_activity_gap_filled(self.chat_id, "Programming")
        
        # New activity should start exactly where the last one ended
        self.assertEqual(activity.start_time, end_time)
        self.assertAlmostEqual(activity.end_time.timestamp(), now.timestamp(), delta=1)
        self.assertEqual(activity.name, "Programming")

    def test_lookback_limit(self):
        # Create an initial activity ending 800 minutes ago (beyond 760m limit)
        end_time = timezone.now() - timedelta(minutes=800)
        Activity.objects.create(
            telegram_chat_id=self.chat_id,
            name="Sleep",
            start_time=end_time - timedelta(minutes=60),
            end_time=end_time
        )
        
        # Log new activity now
        now = timezone.now()
        activity = log_activity_gap_filled(self.chat_id, "Programming")
        
        # Since last activity was too long ago, should start 1 minute ago
        self.assertAlmostEqual((activity.end_time - activity.start_time).total_seconds(), 60, delta=1)
