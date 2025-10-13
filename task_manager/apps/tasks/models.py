from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Task(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    status = models.ForeignKey("statuses.Status", on_delete=models.PROTECT)
    executor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="executed_tasks",
    )
    due_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Deadline for task completion",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the task was marked complete",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="authored_tasks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    labels = models.ManyToManyField(
        "labels.Label", blank=True, related_name="tasks"
    )

    def __str__(self):
        return self.name

    @property
    def is_completed(self):
        return self.completed_at is not None

    @property
    def is_overdue(self):
        if self.completed_at or not self.due_at:
            return False
        return self.due_at < timezone.now()
