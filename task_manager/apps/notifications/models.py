from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Notification(models.Model):
    class Type(models.TextChoices):
        TASK_ASSIGNED = "task_assigned", _("Task assigned")
        TASK_OVERDUE = "task_overdue", _("Task overdue")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    task = models.ForeignKey(
        "tasks.Task",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(max_length=64, choices=Type.choices)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["task", "type"]),
        ]

    def __str__(self):
        return f"{self.get_type_display()} -> {self.user}"

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
