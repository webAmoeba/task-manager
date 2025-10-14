import logging
from datetime import timezone as dt_timezone
from typing import Dict, Optional

import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.utils import timezone

from task_manager.apps.notifications.models import Notification
from task_manager.apps.telegram.models import TelegramProfile

logger = logging.getLogger(__name__)


def serialize_notification(
    notification: Notification,
) -> Dict[str, Optional[str]]:
    def format_dt(value):
        if not value:
            return None
        aware = value
        if timezone.is_naive(aware):
            aware = timezone.make_aware(aware, dt_timezone.utc)
        utc_value = aware.astimezone(dt_timezone.utc)
        return utc_value.isoformat().replace("+00:00", "Z")

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


def send_telegram_notification(notification: Notification) -> None:
    bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        return

    profile = TelegramProfile.objects.filter(
        user=notification.user, is_active=True, chat_id__gt=0
    ).first()
    if not profile:
        return

    message_lines = [f"<b>{notification.title}</b>"]
    if notification.message:
        message_lines.append(notification.message)
    if notification.task_id:
        task_url = (
            settings.SITE_URL.rstrip("/") + f"/tasks/{notification.task_id}/"
        )
        message_lines.append(f"<a href='{task_url}'>View task</a>")

    text = "\n".join(message_lines)

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": profile.chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to send Telegram notification: %s", exc)
