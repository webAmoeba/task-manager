"""
URL configuration for task_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from task_manager import views
from task_manager.apps.users.views import CustomLoginView, CustomLogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("api/", include("task_manager.api.urls")),
    path("users/", include("task_manager.apps.users.urls")),
    path(
        "login/",
        CustomLoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("statuses/", include("task_manager.apps.statuses.urls")),
    path("tasks/", include("task_manager.apps.tasks.urls")),
    path("labels/", include("task_manager.apps.labels.urls")),
]

handler404 = "task_manager.views.custom_404"
