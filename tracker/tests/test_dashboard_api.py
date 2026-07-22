import hashlib
import hmac
import json
from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone

from tracker.models import Activity


@override_settings(TELEGRAM_BOT_API_KEY='test-bot-token', TELEGRAM_AUTH_MAX_AGE_SECONDS=86400)
class DashboardApiTests(TestCase):
    def setUp(self):
        self.chat_id = 1001
        self.other_chat_id = 2002
        now = timezone.now()
        self.activity = Activity.objects.create(
            telegram_chat_id=self.chat_id,
            name='Programming',
            start_time=now - timedelta(hours=1),
            end_time=now,
        )
        Activity.objects.create(
            telegram_chat_id=self.other_chat_id,
            name='Private activity',
            start_time=now - timedelta(hours=1),
            end_time=now,
        )

    def authenticate(self, chat_id=None):
        session = self.client.session
        session['telegram_chat_id'] = chat_id or self.chat_id
        session.save()

    def test_activities_require_an_authenticated_session(self):
        response = self.client.get('/api/activities?chat_id=2002')
        self.assertEqual(response.status_code, 401)

    def test_activities_are_scoped_to_the_session_not_query_parameters(self):
        self.authenticate()
        response = self.client.get('/api/activities?chat_id=2002')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload['activities']), 1)
        self.assertEqual(payload['activities'][0]['displayName'], 'Programming')
        self.assertIn('startTime', payload['activities'][0])
        self.assertNotIn('Private activity', str(payload))

    def test_login_accepts_a_valid_telegram_signature(self):
        payload = {'id': str(self.chat_id), 'first_name': 'Test', 'auth_date': str(int(timezone.now().timestamp()))}
        check_string = '\n'.join(f'{key}={value}' for key, value in sorted(payload.items()))
        secret = hashlib.sha256(b'test-bot-token').digest()
        payload['hash'] = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()

        response = self.client.post('/api/auth/telegram', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['telegram_chat_id'], self.chat_id)

    def test_login_rejects_an_invalid_signature(self):
        payload = {'id': str(self.chat_id), 'auth_date': str(int(timezone.now().timestamp())), 'hash': 'invalid'}
        response = self.client.post('/api/auth/telegram', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 403)
