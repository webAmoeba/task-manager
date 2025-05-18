from django.urls import path

from task_manager.apps.statuses.views import (
    StatusCreateView,
    StatusListView,
)

urlpatterns = [
    path("", StatusListView.as_view(), name="status_list"),
    path("create/", StatusCreateView.as_view(), name="status_create"),
]