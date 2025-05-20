from django.contrib import admin

from task_manager.apps.tasks.models import Task

admin.site.register(Task)
