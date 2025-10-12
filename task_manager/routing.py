from django.urls import path

from task_manager.apps.tasks.consumers import TaskUpdatesConsumer

websocket_urlpatterns = [
    path("ws/tasks/", TaskUpdatesConsumer.as_asgi()),
]
