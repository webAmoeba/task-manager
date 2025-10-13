import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from task_manager.apps.notifications.tasks import (
    send_task_assigned_notification,
)
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


# ------------------------------------------------------------------------------


@receiver(pre_save, sender=Task)
def store_previous_task_state(sender, instance: Task, **kwargs):
    if not instance.pk:
        instance._previous_executor_id = None
        return
    try:
        previous = Task.objects.only("executor_id").get(pk=instance.pk)
        instance._previous_executor_id = previous.executor_id
    except Task.DoesNotExist:
        instance._previous_executor_id = None


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


@receiver(post_save, sender=Task)
def trigger_assignment_notifications(
    sender, instance: Task, created: bool, **kwargs
):
    previous_executor_id = getattr(instance, "_previous_executor_id", None)
    if instance.executor_id and (
        created or previous_executor_id != instance.executor_id
    ):
        send_task_assigned_notification.delay(instance.id)
