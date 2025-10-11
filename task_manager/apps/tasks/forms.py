from django import forms
from django.utils.translation import gettext_lazy as _

from task_manager.apps.tasks.models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "status",
            "executor",
            "due_at",
            "labels",
        ]

    def clean_name(self):
        name = self.cleaned_data["name"]
        qs = Task.objects.exclude(pk=self.instance.pk)
        if qs.filter(name=name).exists():
            raise forms.ValidationError(
                _("Task with this name already exists.")
            )
        return name
