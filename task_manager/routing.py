from django.urls import path

from task_manager.apps.notifications.consumers import UserNotificationsConsumer
from task_manager.apps.tasks.consumers import TaskUpdatesConsumer

websocket_urlpatterns = [
    path("ws/tasks/", TaskUpdatesConsumer.as_asgi()),
    path("ws/notifications/", UserNotificationsConsumer.as_asgi()),
]
