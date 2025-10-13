from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from task_manager.apps.notifications.models import Notification
from task_manager.apps.notifications.tasks import (
    check_overdue_tasks,
    send_task_assigned_notification,
)
from task_manager.apps.statuses.models import Status
from task_manager.apps.tasks.models import Task

User = get_user_model()


class NotificationTasksTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author", email="author@example.com", password="pass"
        )
        self.executor = User.objects.create_user(
            username="executor", email="executor@example.com", password="pass"
        )
        self.status = Status.objects.create(name="In progress")

    def create_task(self, **kwargs):
        defaults = {
            "name": "Sample task",
            "description": "Desc",
            "status": self.status,
            "author": self.author,
        }
        defaults.update(kwargs)
        return Task.objects.create(**defaults)

    def test_send_task_assigned_notification_creates_notification(self):
        task = self.create_task(executor=self.executor)

        send_task_assigned_notification.apply((task.id,))

        notification = Notification.objects.get(user=self.executor, task=task)
        self.assertEqual(notification.type, Notification.Type.TASK_ASSIGNED)
        self.assertFalse(notification.is_read)

    def test_send_task_assigned_notification_skips_if_unread_exists(self):
        task = self.create_task(executor=self.executor)
        initial_count = Notification.objects.filter(
            user=self.executor, task=task
        ).count()
        send_task_assigned_notification.apply((task.id,))

        self.assertEqual(
            Notification.objects.filter(user=self.executor, task=task).count(),
            initial_count,
        )

    def test_check_overdue_tasks_creates_notifications(self):
        overdue_task = self.create_task(
            executor=self.executor,
            due_at=timezone.now() - timedelta(hours=1),
        )

        check_overdue_tasks.apply(())

        self.assertTrue(
            Notification.objects.filter(
                user=self.executor,
                task=overdue_task,
                type=Notification.Type.TASK_OVERDUE,
            ).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                user=self.author,
                task=overdue_task,
                type=Notification.Type.TASK_OVERDUE,
            ).exists()
        )
