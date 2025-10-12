from django.urls import path

from task_manager.apps.tasks.views import (
    TaskCompleteView,
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
)

urlpatterns = [
    path("", TaskListView.as_view(), name="task_list"),
    path("create/", TaskCreateView.as_view(), name="task_create"),
    path(
        "<int:pk>/update/", TaskUpdateView.as_view(), name="task_update"
    ),
    path('<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    path(
        "<int:pk>/complete/",
        TaskCompleteView.as_view(),
        name="task_complete",
    ),
    path("<int:pk>/", TaskDetailView.as_view(), name="task_detail"),
]
