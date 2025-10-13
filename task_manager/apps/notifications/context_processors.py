from task_manager.apps.notifications.models import Notification


def notifications_unread_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
    else:
        count = 0
    return {"notifications_unread_count": count}
