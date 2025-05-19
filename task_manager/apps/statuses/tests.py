from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from task_manager.apps.statuses.models import Status


class StatusCRUDTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

        self.status = Status.objects.create(name="In progress")

    def test_status_list_view(self):
        response = self.client.get(reverse("status_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.status.name)

    def test_status_create(self):
        response = self.client.post(
            reverse("status_create"), {"name": "New status"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Status.objects.filter(name="New status").exists())

    def test_status_update(self):
        response = self.client.post(
            reverse("status_update", args=[self.status.id]),
            {"name": "Updated name"},
        )
        self.assertEqual(response.status_code, 302)
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, "Updated name")

    def test_status_delete(self):
        response = self.client.post(
            reverse("status_delete", args=[self.status.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Status.objects.filter(id=self.status.id).exists())

    def test_unauthorized_redirect(self):
        self.client.logout()
        urls = [
            reverse("status_list"),
            reverse("status_create"),
            reverse("status_update", args=[self.status.id]),
            reverse("status_delete", args=[self.status.id]),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"/login/?next={url}")
