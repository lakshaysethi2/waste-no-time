from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from tracker.models import Activity, Goal
from tracker.trajectory import get_trajectory

class TrajectoryTest(TestCase):
    def setUp(self):
        self.chat_id = 12345
        self.category = "Programming"

    def test_trajectory_simple(self):
        # Goal: 100 hours per month
        Goal.objects.create(
            telegram_chat_id=self.chat_id,
            name="Learn Django",
            category=self.category,
            target_hours=100,
            period='month'
        )
        
        now = timezone.now()
        # Log 10 hours today (start of month)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        Activity.objects.create(
            telegram_chat_id=self.chat_id,
            name=self.category,
            start_time=start_of_month,
            end_time=start_of_month + timedelta(hours=10)
        )
        
        # Add some historical data: average 4 hours per day for last 7 days
        for i in range(1, 8):
            day_start = (now - timedelta(days=i)).replace(hour=8, minute=0)
            Activity.objects.create(
                telegram_chat_id=self.chat_id,
                name=self.category,
                start_time=day_start,
                end_time=day_start + timedelta(hours=4)
            )
            
        traj = get_trajectory(self.chat_id, self.category, 'month')
        
        self.assertEqual(traj['category'], self.category)
        self.assertEqual(traj['actual_so_far_hours'], 38.0)
        self.assertAlmostEqual(traj['recent_pace_hours'], 4.0, delta=0.5)
        
        # Forecast total should be 10 + (4 * remaining_days)
        # Assuming today is early in the month.
        self.assertGreater(traj['forecast_total_hours'], 10)
        self.assertTrue('status' in traj)
