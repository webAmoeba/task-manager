from django.urls import path

from task_manager.apps.notifications.views import (
    NotificationListView,
    NotificationToggleReadView,
)

app_name = "notifications"

urlpatterns = [
    path("", NotificationListView.as_view(), name="list"),
    path(
        "<int:pk>/toggle/", NotificationToggleReadView.as_view(), name="toggle"
    ),
]
