from django.contrib import admin

from task_manager.apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "type",
        "task",
        "is_read",
        "created_at",
    )
    list_filter = ("type", "is_read", "created_at")
    search_fields = ("user__username", "title", "message")
    raw_id_fields = ("user", "task")
