from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from tracker.models import Activity
from tracker.gap_filler import create_activity_with_gap_filling, get_time_spent_today_seconds

class TrackerTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_id = 1040271347

    def test_cold_start_gap_filling(self):
        now = timezone.now()
        act = create_activity_with_gap_filling(self.user_id, "Programming", notes="Coding tests", now=now)
        self.assertEqual(act.name, "Programming")
        self.assertEqual(act.user_id, self.user_id)
        self.assertAlmostEqual((now - act.start_time).total_seconds(), 60, delta=5)

    def test_consecutive_gap_filling(self):
        now = timezone.now()
        act1 = create_activity_with_gap_filling(self.user_id, "Programming", now=now - timedelta(hours=1))
        act2 = create_activity_with_gap_filling(self.user_id, "Walking", now=now)
        
        self.assertEqual(act2.start_time, act1.end_time)

    def test_multi_tenant_isolation(self):
        now = timezone.now()
        create_activity_with_gap_filling(111, "User1Act", now=now)
        create_activity_with_gap_filling(222, "User2Act", now=now)

        self.assertEqual(Activity.objects.filter(user_id=111).count(), 1)
        self.assertEqual(Activity.objects.filter(user_id=222).count(), 1)
        self.assertEqual(Activity.objects.filter(user_id=111).first().name, "User1Act")

    def test_dashboard_and_api(self):
        create_activity_with_gap_filling(self.user_id, "Reading", now=timezone.now())
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        api_resp = self.client.get('/api/activities/')
        self.assertEqual(api_resp.status_code, 200)
        data = api_resp.json()
        self.assertIn("activities", data)
        self.assertGreaterEqual(len(data["activities"]), 1)
