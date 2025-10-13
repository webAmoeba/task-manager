from django.utils import timezone
from rest_framework import serializers

from task_manager.apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    read_at = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "type",
            "title",
            "message",
            "task",
            "is_read",
            "created_at",
            "read_at",
            "payload",
        ]
        read_only_fields = fields

    def get_created_at(self, obj):
        return self._format_dt(obj.created_at)

    def get_read_at(self, obj):
        return self._format_dt(obj.read_at)

    def _format_dt(self, value):
        if not value:
            return None
        aware = value
        if timezone.is_naive(aware):
            aware = timezone.make_aware(aware, timezone.utc)
        utc_value = aware.astimezone(timezone.utc)
        return utc_value.isoformat().replace("+00:00", "Z")
