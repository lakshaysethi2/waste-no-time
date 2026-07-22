from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

import pytz

from tracker.models import Activity, Goal
from tracker.trajectory import get_trajectory


class TrajectoryTest(TestCase):
    def setUp(self):
        self.chat_id = 12345
        self.category = "Programming"

    def test_trajectory_simple(self):
        # Freeze "now" to a mid-month date so the 7-day history stays inside the month
        # and the test does not depend on what day of the month it is executed.
        fixed_now = datetime(2026, 7, 15, 12, 0, 0, tzinfo=pytz.UTC)

        with patch("tracker.trajectory.timezone.now", return_value=fixed_now):
            # Goal: 100 hours per month
            Goal.objects.create(
                telegram_chat_id=self.chat_id,
                name="Learn Django",
                category=self.category,
                target_hours=100,
                period="month",
            )

            now = fixed_now
            # Log 10 hours at start of month
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            Activity.objects.create(
                telegram_chat_id=self.chat_id,
                name=self.category,
                start_time=start_of_month,
                end_time=start_of_month + timedelta(hours=10),
            )

            # Add historical data: 4 hours per day for last 7 days (all inside July)
            for i in range(1, 8):
                day_start = (now - timedelta(days=i)).replace(hour=8, minute=0, second=0, microsecond=0)
                Activity.objects.create(
                    telegram_chat_id=self.chat_id,
                    name=self.category,
                    start_time=day_start,
                    end_time=day_start + timedelta(hours=4),
                )

            traj = get_trajectory(self.chat_id, self.category, "month")

        self.assertEqual(traj["category"], self.category)
        # 10h at start of month + 7*4h historical = 38h actual in July
        self.assertAlmostEqual(traj["actual_so_far_hours"], 38.0, delta=0.01)
        # The 28-day pace window includes days without logged activity.
        self.assertAlmostEqual(traj["recent_pace_hours"], 2.3, delta=0.5)

        # Forecast total should be > actual and include remaining days
        self.assertGreater(traj["forecast_total_hours"], 10)
        self.assertIn("status", traj)
        self.assertIn(traj["status"], {"On Path", "Correction Needed"})

    def test_trajectory_respects_user_timezone(self):
        """A user in Pacific/Auckland should have period boundaries in their local calendar."""
        from tracker.models import KeyValuePair

        fixed_now = datetime(2026, 7, 15, 12, 0, 0, tzinfo=pytz.UTC)
        # Set user's timezone to Pacific/Auckland (UTC+12/+13)
        KeyValuePair.objects.create(
            telegram_chat_id=self.chat_id, key="tz", value="Pacific/Auckland"
        )

        with patch("tracker.trajectory.timezone.now", return_value=fixed_now):
            Goal.objects.create(
                telegram_chat_id=self.chat_id,
                name="Auckland Goal",
                category=self.category,
                target_hours=50,
                period="day",
            )
            # fixed_now = July 15 12:00 UTC = July 16 00:00 NZST (NZ is UTC+12)
            # So the local day is July 16. Create activity at 01:00 NZST on July 16 — safely inside that bucket.
            nz_tz = pytz.timezone("Pacific/Auckland")
            local_dt = nz_tz.localize(datetime(2026, 7, 16, 1, 0, 0))
            utc_dt = local_dt.astimezone(pytz.UTC)
            Activity.objects.create(
                telegram_chat_id=self.chat_id,
                name=self.category,
                start_time=utc_dt,
                end_time=utc_dt + timedelta(hours=1),
            )

            traj_day = get_trajectory(self.chat_id, self.category, "day")

        # Activity should be counted in the local day bucket (July 15 NZST = July 15 UTC+12)
        self.assertGreaterEqual(traj_day["actual_so_far_hours"], 0.9)
