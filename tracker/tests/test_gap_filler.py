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

    def test_merge_same_name_within_10_min(self):
        # Create an initial activity ending 2 minutes ago
        past = timezone.now() - timedelta(minutes=2)
        original = Activity.objects.create(
            telegram_chat_id=self.chat_id,
            name="Programming",
            start_time=past - timedelta(minutes=5),
            end_time=past
        )

        # Log the same activity now — should merge (extend) the existing one
        now = timezone.now()
        activity = log_activity_gap_filled(self.chat_id, "Programming")

        # Should return the SAME record, with end_time updated
        self.assertEqual(activity.pk, original.pk)
        self.assertAlmostEqual(activity.end_time.timestamp(), now.timestamp(), delta=1)

        # Verify only 1 activity exists for this chat
        count = Activity.objects.filter(telegram_chat_id=self.chat_id).count()
        self.assertEqual(count, 1)

    def test_no_merge_different_name(self):
        # Create an initial activity ending 2 minutes ago
        past = timezone.now() - timedelta(minutes=2)
        Activity.objects.create(
            telegram_chat_id=self.chat_id,
            name="Sleep",
            start_time=past - timedelta(minutes=30),
            end_time=past
        )

        # Log a different activity — should NOT merge
        activity = log_activity_gap_filled(self.chat_id, "Programming")
        self.assertEqual(activity.name, "Programming")

        # Verify 2 activities exist
        count = Activity.objects.filter(telegram_chat_id=self.chat_id).count()
        self.assertEqual(count, 2)

    def test_no_merge_gap_exceeds_10_min(self):
        # Create an initial activity ending 15 minutes ago (> 10 min gap)
        past = timezone.now() - timedelta(minutes=15)
        original = Activity.objects.create(
            telegram_chat_id=self.chat_id,
            name="Programming",
            start_time=past - timedelta(minutes=30),
            end_time=past
        )

        # Log the same activity now — gap > 10 min, should NOT merge
        activity = log_activity_gap_filled(self.chat_id, "Programming")
        self.assertNotEqual(activity.pk, original.pk)
        self.assertEqual(activity.name, "Programming")

        # Verify 2 activities exist
        count = Activity.objects.filter(telegram_chat_id=self.chat_id).count()
        self.assertEqual(count, 2)

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
