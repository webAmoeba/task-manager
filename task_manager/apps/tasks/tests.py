from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

# todo: add tests with labels
# from task_manager.apps.labels.models import Label
from task_manager.apps.statuses.models import Status
from task_manager.apps.tasks.models import Task


class TaskCRUDTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author", password="pass"
        )
        self.executor = User.objects.create_user(
            username="executor", password="pass"
        )
        self.status = Status.objects.create(name="In Progress")
        # self.label = Label.objects.create(name="Bug")
        self.task = Task.objects.create(
            name="Fix bug",
            description="Critical issue",
            status=self.status,
            author=self.author,
            executor=self.executor,
        )
        self.client.force_login(self.author)

    def test_task_list_view(self):
        response = self.client.get(reverse("task_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.name)

    def test_create_task(self):
        response = self.client.post(
            reverse("task_create"),
            {
                "name": "New Task",
                "description": "Do something",
                "status": self.status.id,
                "executor": self.executor.id,
                # "labels": [self.label.id],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New Task")
        self.assertTrue(Task.objects.filter(name="New Task").exists())

    def test_update_task(self):
        response = self.client.post(
            reverse("task_update", args=[self.task.id]),
            {
                "name": "Updated Task",
                "description": "Updated desc",
                "status": self.status.id,
                "executor": self.executor.id,
                # "labels": [self.label.id],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Updated Task")
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, "Updated Task")

    def test_delete_task_by_author(self):
        response = self.client.post(
            reverse("task_delete", args=[self.task.id]), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Task successfully deleted"
        )
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_delete_task_forbidden_for_not_author(self):
        self.client.logout()
        self.client.force_login(self.executor)
        response = self.client.post(reverse("task_delete", args=[self.task.id]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Task.objects.filter(id=self.task.id).exists())
