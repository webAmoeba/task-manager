from django import forms
from django.utils.translation import gettext_lazy as _

from task_manager.apps.labels.models import Label


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ["name"]

    def clean_name(self):
        name = self.cleaned_data["name"]
        qs = Label.objects.exclude(pk=self.instance.pk)
        if qs.filter(name=name).exists():
            raise forms.ValidationError(
                _("Label with this name already exists.")
            )
        return name
