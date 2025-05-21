from django.contrib.auth import get_user_model
from django.db import models

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
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="authored_tasks"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
