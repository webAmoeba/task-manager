from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from task_manager.apps.labels.models import Label
from task_manager.apps.statuses.models import Status
from task_manager.apps.tasks.models import Task


class LabelCRUDTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.client.login(username="testuser", password="testpass")

    def test_create_label(self):
        response = self.client.post(reverse("label_create"), {"name": "Bug"})
        self.assertRedirects(response, reverse("label_list"))
        self.assertTrue(Label.objects.filter(name="Bug").exists())

    def test_list_labels(self):
        Label.objects.create(name="Feature")
        response = self.client.get(reverse("label_list"))
        self.assertContains(response, "Feature")

    def test_update_label(self):
        label = Label.objects.create(name="Initial")
        response = self.client.post(
            reverse("label_update", args=[label.pk]), {"name": "Updated"}
        )
        self.assertRedirects(response, reverse("label_list"))
        label.refresh_from_db()
        self.assertEqual(label.name, "Updated")

    def test_delete_label_not_in_use(self):
        label = Label.objects.create(name="Temporary")
        response = self.client.post(reverse("label_delete", args=[label.pk]))
        self.assertRedirects(response, reverse("label_list"))
        self.assertFalse(Label.objects.filter(pk=label.pk).exists())

    def test_delete_label_in_use(self):
        label = Label.objects.create(name="In Use")
        status = Status.objects.create(name="Open")
        Task.objects.create(
            name="Task with label", status=status, author=self.user
        )
        task = Task.objects.first()
        task.labels.add(label)

        response = self.client.post(reverse("label_delete", args=[label.pk]))
        self.assertRedirects(response, reverse("label_list"))
        self.assertTrue(Label.objects.filter(pk=label.pk).exists())
        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any("not possible to delete" in str(m) for m in messages)
        )
