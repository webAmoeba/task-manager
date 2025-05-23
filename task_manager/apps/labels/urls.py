from django.urls import path

from task_manager.apps.labels.views import LabelCreateView, LabelListView

urlpatterns = [
    path("", LabelListView.as_view(), name="label_list"),
    path("create/", LabelCreateView.as_view(), name="label_create"),
]