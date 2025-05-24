from django import forms
from django.utils.translation import gettext_lazy as _

from task_manager.apps.statuses.models import Status


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ["name"]

    def clean_name(self):
        name = self.cleaned_data["name"]
        qs = Status.objects.exclude(pk=self.instance.pk)
        if qs.filter(name=name).exists():
            raise forms.ValidationError(
                _("Status with this name already exists.")
            )
        return name
