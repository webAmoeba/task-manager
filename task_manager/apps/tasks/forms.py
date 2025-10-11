from django import forms
from django.utils import timezone
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
        widgets = {
            "due_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"]
        qs = Task.objects.exclude(pk=self.instance.pk)
        if qs.filter(name=name).exists():
            raise forms.ValidationError(
                _("Task with this name already exists.")
            )
        return name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        due_field = self.fields.get("due_at")
        if due_field:
            due_field.required = False
            due_field.input_formats = ["%Y-%m-%dT%H:%M"]
            if self.instance.pk and self.instance.due_at:
                original_due = self.instance.due_at
                if timezone.is_naive(original_due):
                    local_due = original_due
                else:
                    local_due = timezone.localtime(original_due)
                self.initial["due_at"] = local_due.strftime("%Y-%m-%dT%H:%M")
