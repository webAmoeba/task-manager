from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from task_manager.apps.labels.forms import LabelForm
from task_manager.apps.labels.models import Label
from task_manager.apps.tasks.models import Task


class CustomLoginRequiredMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        messages.error(
            self.request, _("You are not authorized! Please log in.")
        )
        path = self.request.get_full_path()
        login_url = self.get_login_url()
        return redirect(f"{login_url}?{urlencode({'next': path})}")


class LabelListView(CustomLoginRequiredMixin, ListView):
    model = Label
    template_name = "labels/label_list.html"
    context_object_name = "labels"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Labels")

        used_label_ids = Task.objects.values_list(
            "labels", flat=True
        ).distinct()
        context["used_label_ids"] = set(filter(None, used_label_ids))

        return context


class LabelCreateView(
    CustomLoginRequiredMixin, SuccessMessageMixin, CreateView
):
    model = Label
    form_class = LabelForm
    template_name = "labels/label_form.html"
    success_url = reverse_lazy("label_list")

    def form_valid(self, form):
        messages.success(self.request, _("Label created successfully"))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create label")
        context["is_create_view"] = True
        return context


class LabelUpdateView(CustomLoginRequiredMixin, UpdateView):
    model = Label
    template_name = "labels/label_form.html"
    form_class = LabelForm
    success_url = reverse_lazy("label_list")

    def form_valid(self, form):
        messages.success(self.request, _("Label successfully updated"))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Update label")
        context["is_create_view"] = False
        return context


class LabelDeleteView(
    CustomLoginRequiredMixin, SuccessMessageMixin, DeleteView
):
    model = Label
    template_name = "labels/label_delete.html"
    success_url = reverse_lazy("label_list")
    success_message = _("Label successfully deleted")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Deleting a label")
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.tasks.exists():
            messages.error(
                request,
                _("It is not possible to delete a label, because it is in use"),
            )
            return redirect(self.success_url)

        messages.success(request, self.success_message)
        return super().post(request, *args, **kwargs)
