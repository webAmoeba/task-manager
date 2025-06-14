from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from task_manager.apps.statuses.forms import StatusForm
from task_manager.apps.statuses.models import Status
from task_manager.apps.tasks.models import Task


class CustomLoginRequiredMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        messages.error(
            self.request, _("You are not authorized! Please log in.")
        )
        path = self.request.get_full_path()
        login_url = self.get_login_url()
        return redirect(f"{login_url}?{urlencode({'next': path})}")


class StatusListView(CustomLoginRequiredMixin, ListView):
    model = Status
    template_name = "statuses/status_list.html"
    context_object_name = "statuses"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Statuses")

        used_status_ids = Task.objects.values_list(
            "status_id", flat=True
        ).distinct()
        context["used_status_ids"] = set(used_status_ids)

        return context


class StatusCreateView(
    CustomLoginRequiredMixin, SuccessMessageMixin, CreateView
):
    model = Status
    form_class = StatusForm
    template_name = "statuses/status_form.html"
    success_url = reverse_lazy("status_list")

    def form_valid(self, form):
        messages.success(self.request, _("Status created successfully"))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create status")
        context["is_create_view"] = True
        return context


class StatusUpdateView(CustomLoginRequiredMixin, UpdateView):
    model = Status
    template_name = "statuses/status_form.html"
    form_class = StatusForm
    success_url = reverse_lazy("status_list")

    def form_valid(self, form):
        messages.success(self.request, _("Status successfully updated"))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Update status")
        context["is_create_view"] = False
        return context


class StatusDeleteView(
    CustomLoginRequiredMixin, SuccessMessageMixin, DeleteView
):
    model = Status
    template_name = "statuses/status_delete.html"
    success_url = reverse_lazy("status_list")
    success_message = _("Status successfully deleted")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Deleting a status")
        return context

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(
                self.request,
                _(
                    "It is not possible to delete a status, "
                    "because it is in use"
                ),
            )
            return redirect(self.success_url)
