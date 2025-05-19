from django.urls import path

from task_manager.apps.statuses.views import (
    StatusCreateView,
    StatusDeleteView,
    StatusListView,
    StatusUpdateView,
)

urlpatterns = [
    path("", StatusListView.as_view(), name="status_list"),
    path("create/", StatusCreateView.as_view(), name="status_create"),
    path("<int:pk>/update/", StatusUpdateView.as_view(), name="status_update"),
    path('<int:pk>/delete/', StatusDeleteView.as_view(), name='status_delete'),
]