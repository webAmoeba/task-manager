from django.urls import path

from task_manager.apps.tasks.views import TaskListView

urlpatterns = [
    path("", TaskListView.as_view(), name="task_list"),
]
