from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from task_manager.apps.tasks.api.serializers import TaskSerializer
from task_manager.apps.tasks.models import Task


class TaskPermission(permissions.BasePermission):
    """
    Allow read for authenticated users.
    Mutations restricted to task author unless action-specific rule applies.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if view.action == "complete":
            return request.user in {obj.author, obj.executor}

        if view.action == "destroy":
            return obj.author == request.user

        # update / partial_update
        if view.action in {"update", "partial_update"}:
            return obj.author == request.user

        return True


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [TaskPermission]

    def get_queryset(self):
        queryset = (
            Task.objects.select_related("status", "author", "executor")
            .prefetch_related("labels")
            .order_by("-created_at")
        )

        params = self.request.query_params
        status_id = params.get("status")
        executor_id = params.get("executor")
        label_id = params.get("label")
        self_tasks = params.get("self_tasks")
        assigned = params.get("assigned")
        completed = params.get("completed")

        if status_id:
            queryset = queryset.filter(status_id=status_id)
        if executor_id:
            queryset = queryset.filter(executor_id=executor_id)
        if label_id:
            queryset = queryset.filter(labels__id=label_id)

        if self_tasks in {"1", "true", "True"}:
            queryset = queryset.filter(author=self.request.user)

        if assigned in {"1", "true", "True"}:
            queryset = queryset.filter(executor=self.request.user)

        if completed in {"1", "true", "True"}:
            queryset = queryset.filter(completed_at__isnull=False)
        elif completed in {"0", "false", "False"}:
            queryset = queryset.filter(completed_at__isnull=True)

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()

        if task.completed_at:
            serializer = self.get_serializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)

        task.completed_at = timezone.now()
        task.save(update_fields=["completed_at"])
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
