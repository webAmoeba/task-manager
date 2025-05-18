from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from task_manager.apps.statuses.models import Status


class CustomLoginRequiredMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        messages.error(
            self.request, _("You are not authorized! Please log in.")
        )
        return redirect(self.get_login_url())


class StatusListView(CustomLoginRequiredMixin, ListView):
    model = Status
    template_name = "statuses/status_list.html"
    context_object_name = "statuses"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Statuses")
        return context


class StatusCreateView(
    CustomLoginRequiredMixin, SuccessMessageMixin, CreateView
):
    model = Status
    template_name = "statuses/status_form.html"
    fields = ["name"]
    success_url = reverse_lazy("status_list")
    success_message = _("Status created successfully")
