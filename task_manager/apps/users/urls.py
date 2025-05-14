from django.urls import path

from task_manager.apps.users.views import UserCreateView, UserListView

urlpatterns = [
    path("", UserListView.as_view(), name="user_list"),
    path("create/", UserCreateView.as_view(), name="user_create"),
]
