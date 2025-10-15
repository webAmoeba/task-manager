from __future__ import annotations

from typing import Iterable

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone, translation
from django.utils.translation import gettext as _

from task_manager.apps.notifications.models import Notification
from task_manager.apps.notifications.services import (
    broadcast_notification,
    send_telegram_notification,
)

User = get_user_model()


def _create_notification(
    *,
    user: User,
    notif_type: str,
    title: str,
    message: str = "",
    task=None,
    payload=None,
) -> Notification:
    if payload is None:
        payload = {}
    notification = Notification.objects.create(
        user=user,
        task=task,
        type=notif_type,
        title=title,
        message=message,
        payload=payload,
    )
    broadcast_notification(notification)
    send_telegram_notification(notification)
    return notification


@shared_task
def send_task_assigned_notification(task_id: int):
    from task_manager.apps.tasks.models import Task

    try:
        task = (
            Task.objects.select_related("executor", "author")
            .only(
                "id",
                "name",
                "executor__id",
                "executor__username",
                "author__username",
            )
            .get(pk=task_id)
        )
    except Task.DoesNotExist:
        return

    if not task.executor:
        return

    has_unread = Notification.objects.filter(
        user=task.executor,
        task=task,
        type=Notification.Type.TASK_ASSIGNED,
        is_read=False,
    ).exists()
    if has_unread:
        return

    # Ensure translations are evaluated under Russian locale in background task
    with translation.override("ru"):
        title = _('You have been assigned to task "%(name)s"') % {
            "name": task.name
        }
        message = _("Author: %(author)s") % {
            "author": task.author.get_username()
        }
    _create_notification(
        user=task.executor,
        notif_type=Notification.Type.TASK_ASSIGNED,
        title=title,
        message=message,
        task=task,
        payload={"task_id": task.id},
    )


@shared_task
def check_overdue_tasks():
    from task_manager.apps.tasks.models import Task

    now = timezone.now()
    overdue_tasks = Task.objects.select_related("executor", "author").filter(
        due_at__isnull=False, due_at__lt=now, completed_at__isnull=True
    )

    for task in overdue_tasks:
        recipients: Iterable[User] = filter(
            None,
            {
                task.executor,
                task.author,
            },
        )
        for user in recipients:
            exists = Notification.objects.filter(
                user=user,
                task=task,
                type=Notification.Type.TASK_OVERDUE,
                is_read=False,
            ).exists()
            if exists:
                continue
            # Force Russian locale while composing notification texts
            with translation.override("ru"):
                title = _('Task "%(name)s" is overdue') % {"name": task.name}
                message = _(
                    "Deadline %(deadline)s has passed. Please complete or update the task."  # noqa: E501
                ) % {
                    "deadline": timezone.localtime(task.due_at).strftime(
                        "%d.%m.%Y %H:%M"
                    )
                }
            _create_notification(
                user=user,
                notif_type=Notification.Type.TASK_OVERDUE,
                title=title,
                message=message,
                task=task,
                payload={"task_id": task.id},
            )
