from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "task_manager.apps.tasks"

    def ready(self):
        # Import signals to ensure task events broadcast over Channels.
        from task_manager.apps.tasks import signals  # noqa: F401
