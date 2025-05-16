from django.utils.translation import gettext as _
from django.views.generic import ListView

from task_manager.apps.statuses.models import Status


class StatusListView(ListView):
    model = Status
    template_name = "statuses/status_list.html"
    context_object_name = "statuses"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Statuses")
        return context
