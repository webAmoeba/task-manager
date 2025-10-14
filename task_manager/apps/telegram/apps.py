from django.apps import AppConfig


class TelegramConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "task_manager.apps.telegram"
    verbose_name = "Telegram Integration"
