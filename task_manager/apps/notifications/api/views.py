from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from task_manager.apps.notifications.api.serializers import (
    NotificationSerializer,
)
from task_manager.apps.notifications.models import Notification


class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )
        unread = self.request.query_params.get("unread")
        if unread is not None:
            if unread in {"1", "true", "True"}:
                queryset = queryset.filter(is_read=False)
            elif unread in {"0", "false", "False"}:
                queryset = queryset.filter(is_read=True)
        return queryset

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.mark_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
