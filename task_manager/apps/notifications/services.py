import logging
from typing import Dict, Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from task_manager.apps.notifications.models import Notification

logger = logging.getLogger(__name__)


def serialize_notification(
    notification: Notification,
) -> Dict[str, Optional[str]]:
    created_at = notification.created_at
    read_at = notification.read_at
    return {
        "id": notification.id,
        "type": notification.type,
        "title": notification.title,
        "message": notification.message,
        "task_id": notification.task_id,
        "is_read": notification.is_read,
        "created_at": created_at.isoformat() if created_at else None,
        "read_at": read_at.isoformat() if read_at else None,
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
