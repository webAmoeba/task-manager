from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from task_manager.apps.labels.models import Label
from task_manager.apps.statuses.models import Status
from task_manager.apps.tasks.models import Task

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    labels = serializers.PrimaryKeyRelatedField(
        queryset=Label.objects.all(),
        many=True,
        required=False,
    )
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all())
    executor = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        required=False,
        queryset=User.objects.all(),
    )
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "description",
            "status",
            "executor",
            "author",
            "due_at",
            "completed_at",
            "is_completed",
            "created_at",
            "labels",
        ]
        read_only_fields = [
            "id",
            "author",
            "completed_at",
            "is_completed",
            "created_at",
        ]

    def get_is_completed(self, obj):
        return obj.is_completed

    def validate_due_at(self, value):
        if value and timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return value

    def create(self, validated_data):
        labels = validated_data.pop("labels", [])
        request = self.context["request"]
        task = Task.objects.create(author=request.user, **validated_data)
        if labels:
            task.labels.set(labels)
        return task

    def update(self, instance, validated_data):
        labels = validated_data.pop("labels", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if labels is not None:
            instance.labels.set(labels)
        return instance
