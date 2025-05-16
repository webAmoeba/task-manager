from django.urls import path

from task_manager.apps.statuses.views import (
    StatusListView,
)

urlpatterns = [
    path("", StatusListView.as_view(), name="status_list"),
]
