from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from task_manager.apps.labels.models import Label
from task_manager.apps.statuses.models import Status
from task_manager.apps.tasks.models import Task

User = get_user_model()


class TaskAPITests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author_api", password="pass"
        )
        self.executor = User.objects.create_user(
            username="executor_api", password="pass"
        )
        self.other = User.objects.create_user(
            username="other_api", password="pass"
        )
        self.status = Status.objects.create(name="Todo")
        self.label = Label.objects.create(name="API")

        self.task = Task.objects.create(
            name="API Task",
            description="Test task",
            status=self.status,
            author=self.author,
            executor=self.executor,
        )
        self.task.labels.add(self.label)

        self.author_token = Token.objects.create(user=self.author)
        self.executor_token = Token.objects.create(user=self.executor)
        self.other_token = Token.objects.create(user=self.other)

    def auth_headers(self, token):
        return {"HTTP_AUTHORIZATION": f"Token {token.key}"}

    def test_list_requires_authentication(self):
        response = self.client.get(reverse("task-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_returns_tasks(self):
        response = self.client.get(
            reverse("task-list"), **self.auth_headers(self.author_token)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "API Task")

    def test_create_task_sets_author(self):
        payload = {
            "name": "Created via API",
            "description": "Descriptor",
            "status": self.status.id,
            "executor": self.executor.id,
            "labels": [self.label.id],
            "due_at": (timezone.now() + timedelta(days=2)).isoformat(),
        }
        response = self.client.post(
            reverse("task-list"),
            data=payload,
            format="json",
            **self.auth_headers(self.author_token),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Task.objects.get(name="Created via API")
        self.assertEqual(created.author, self.author)
        self.assertEqual(
            list(created.labels.values_list("id", flat=True)), [self.label.id]
        )

    def test_delete_forbidden_for_non_author(self):
        response = self.client.delete(
            reverse("task-detail", args=[self.task.id]),
            **self.auth_headers(self.executor_token),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

    def test_complete_by_executor(self):
        response = self.client.post(
            reverse("task-complete", args=[self.task.id]),
            **self.auth_headers(self.executor_token),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertIsNotNone(self.task.completed_at)

    def test_complete_forbidden_for_other(self):
        response = self.client.post(
            reverse("task-complete", args=[self.task.id]),
            **self.auth_headers(self.other_token),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.task.refresh_from_db()
        self.assertIsNone(self.task.completed_at)
