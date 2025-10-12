import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from task_manager.apps.tasks.api.serializers import TaskSerializer
from task_manager.apps.tasks.models import Task

logger = logging.getLogger(__name__)

GROUP_NAME = "tasks_updates"


def _send_to_channel_layer(message_type: str, event: str, payload: dict):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    try:
        async_to_sync(channel_layer.group_send)(
            GROUP_NAME,
            {
                "type": message_type,
                "event": event,
                "task": payload,
            },
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("Channel layer send failed: %s", exc)


@receiver(post_save, sender=Task)
def broadcast_task_update(sender, instance: Task, created: bool, **kwargs):
    serializer = TaskSerializer(instance)
    payload = serializer.data
    event = "created" if created else "updated"
    _send_to_channel_layer("task_update", event, payload)


@receiver(post_delete, sender=Task)
def broadcast_task_delete(sender, instance: Task, **kwargs):
    payload = {"id": instance.id}
    _send_to_channel_layer("task_delete", "deleted", payload)
