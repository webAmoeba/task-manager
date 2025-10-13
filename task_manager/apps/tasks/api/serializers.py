from datetime import timezone as dt_timezone

from django.contrib.auth import get_user_model
from django.urls import reverse
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
    status_name = serializers.CharField(source="status.name", read_only=True)
    author_full_name = serializers.SerializerMethodField()
    author_username = serializers.SerializerMethodField()
    executor_full_name = serializers.SerializerMethodField()
    executor_username = serializers.SerializerMethodField()
    label_names = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()
    update_url = serializers.SerializerMethodField()
    delete_url = serializers.SerializerMethodField()
    complete_url = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "description",
            "status",
            "status_name",
            "executor",
            "executor_full_name",
            "executor_username",
            "author",
            "author_full_name",
            "author_username",
            "due_at",
            "completed_at",
            "is_completed",
            "created_at",
            "labels",
            "label_names",
            "detail_url",
            "update_url",
            "delete_url",
            "complete_url",
            "is_overdue",
        ]
        read_only_fields = [
            "id",
            "author",
            "author_full_name",
            "author_username",
            "executor_full_name",
            "executor_username",
            "completed_at",
            "is_completed",
            "created_at",
            "status_name",
            "label_names",
            "detail_url",
            "update_url",
            "delete_url",
            "complete_url",
            "is_overdue",
        ]

    def get_is_completed(self, obj):
        return obj.is_completed

    def get_author_full_name(self, obj):
        return obj.author.get_full_name()

    def get_author_username(self, obj):
        return obj.author.username

    def get_executor_full_name(self, obj):
        if obj.executor:
            return obj.executor.get_full_name()
        return None

    def get_executor_username(self, obj):
        if obj.executor:
            return obj.executor.username
        return None

    def get_label_names(self, obj):
        return list(obj.labels.values_list("name", flat=True))

    def get_detail_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(
            reverse("task_detail", args=[obj.pk])
        ) if request else reverse("task_detail", args=[obj.pk])

    def get_update_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(
            reverse("task_update", args=[obj.pk])
        ) if request else reverse("task_update", args=[obj.pk])

    def get_delete_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(
            reverse("task_delete", args=[obj.pk])
        ) if request else reverse("task_delete", args=[obj.pk])

    def get_complete_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(
            reverse("task_complete", args=[obj.pk])
        ) if request else reverse("task_complete", args=[obj.pk])

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        def format_dt(value):
            if not value:
                return None
            aware = value
            if timezone.is_naive(aware):
                aware = timezone.make_aware(aware, dt_timezone.utc)
            utc_value = aware.astimezone(dt_timezone.utc)
            iso = utc_value.isoformat()
            return iso.replace("+00:00", "Z")

        for field in ("due_at", "completed_at", "created_at"):
            representation[field] = format_dt(getattr(instance, field))

        return representation
