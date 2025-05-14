from django.urls import path

from task_manager.apps.users.views import UserCreateView, UserListView, UserUpdateView

urlpatterns = [
    path("", UserListView.as_view(), name="user_list"),
    path("create/", UserCreateView.as_view(), name="user_create"),
    path("<int:pk>/update/", UserUpdateView.as_view(), name="user_update"),
]
