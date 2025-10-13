from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from task_manager.apps.notifications.models import Notification

User = get_user_model()


class NotificationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", password="pass", email="u1@example.com"
        )
        self.other = User.objects.create_user(
            username="user2", password="pass", email="u2@example.com"
        )

        self.notification = Notification.objects.create(
            user=self.user,
            type=Notification.Type.TASK_ASSIGNED,
            title="Assigned",
        )
        Notification.objects.create(
            user=self.other,
            type=Notification.Type.TASK_ASSIGNED,
            title="Other user",
        )

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def test_list_notifications(self):
        self.authenticate()
        response = self.client.get("/api/notifications/?unread=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        results = data["results"] if isinstance(data, dict) else data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.notification.id)

    def test_mark_read(self):
        self.authenticate()
        response = self.client.post(
            f"/api/notifications/{self.notification.id}/mark-read/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

