import logging
from typing import Dict, Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from task_manager.apps.notifications.models import Notification

logger = logging.getLogger(__name__)


def serialize_notification(
    notification: Notification,
) -> Dict[str, Optional[str]]:
    def format_dt(value):
        if not value:
            return None
        aware = value
        if timezone.is_naive(aware):
            aware = timezone.make_aware(
                aware, timezone.get_current_timezone()
            )
        return timezone.localtime(aware).isoformat()

    return {
        "id": notification.id,
        "type": notification.type,
        "title": notification.title,
        "message": notification.message,
        "task_id": notification.task_id,
        "is_read": notification.is_read,
        "created_at": format_dt(notification.created_at),
        "read_at": format_dt(notification.read_at),
        "payload": notification.payload,
    }


def broadcast_notification(notification: Notification) -> None:
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    try:
        async_to_sync(channel_layer.group_send)(
            f"user_notifications_{notification.user_id}",
            {
                "type": "notification_event",
                "notification": serialize_notification(notification),
            },
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("Notification broadcast failed: %s", exc)
