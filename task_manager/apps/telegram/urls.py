from django.urls import path

from task_manager.apps.telegram.views import TelegramSettingsView

app_name = "telegram"

urlpatterns = [
    path("", TelegramSettingsView.as_view(), name="settings"),
]
