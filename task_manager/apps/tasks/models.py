from django.contrib.auth import get_user_model
from django.db import models

from task_manager.apps.statuses.models import Status

User = get_user_model()


class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.ForeignKey(
        Status, on_delete=models.PROTECT, verbose_name="Status"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="authored_tasks",
        verbose_name="Author",
    )
    executor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="executed_tasks",
        blank=True,
        null=True,
        verbose_name="Executor",
    )
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
