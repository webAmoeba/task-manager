from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from task_manager.apps.tasks.api.views import TaskViewSet

router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("auth/token/", obtain_auth_token, name="api_token_auth"),
    path("", include(router.urls)),
]
