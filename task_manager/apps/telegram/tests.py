from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from task_manager.apps.telegram.models import BotToken

User = get_user_model()


class TelegramSettingsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="telegram_user",
            password="pass123",
            email="telegram@example.com",
        )
        self.client = Client()

    def test_requires_login(self):
        response = self.client.get(reverse("telegram:settings"))
        self.assertEqual(response.status_code, 302)

    def test_generate_token(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("telegram:settings"), {"action": "generate_token"}
        )
        self.assertEqual(response.status_code, 302)
        token = BotToken.objects.filter(user=self.user, is_active=True).first()
        self.assertIsNotNone(token)
