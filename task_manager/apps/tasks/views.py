from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from task_manager.apps.statuses.models import Status
from task_manager.apps.tasks.forms import TaskForm
from task_manager.apps.tasks.models import Task

User = get_user_model()


class CustomLoginRequiredMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        messages.error(
            self.request, _("You are not authorized! Please log in.")
        )
        path = self.request.get_full_path()
        login_url = self.get_login_url()
        return redirect(f"{login_url}?{urlencode({'next': path})}")


class TaskListView(CustomLoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"
    template_name = "tasks/task_list.html"

    def get_queryset(self):
        queryset = Task.objects.select_related("status", "author", "executor")
        status = self.request.GET.get("status")
        executor = self.request.GET.get("executor")
        label = self.request.GET.get("label")
        self_tasks = self.request.GET.get("self_tasks")

        if status:
            queryset = queryset.filter(status_id=status)
        if executor:
            queryset = queryset.filter(executor_id=executor)
        if label:
            queryset = queryset.filter(labels__id=label)
        if self_tasks:
            queryset = queryset.filter(author=self.request.user)

        return queryset.distinct().order_by("id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Tasks")
        context["statuses"] = Status.objects.all()
        context["users"] = get_user_model().objects.all()
        return context


class TaskCreateView(CustomLoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, _("Task created successfully"))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create task")
        context["is_create_view"] = True
        context["statuses"] = Status.objects.all()
        context["executors"] = User.objects.all()
        return context


class TaskUpdateView(CustomLoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("task_list")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, _("Task successfully updated"))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Edit task")
        context["is_create_view"] = False
        context["statuses"] = context["form"].fields["status"].queryset
        context["executors"] = context["form"].fields["executor"].queryset
        return context


class TaskDeleteView(CustomLoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Task
    template_name = "tasks/task_delete.html"
    success_url = reverse_lazy("task_list")
    success_message = _("Task successfully deleted")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Deleting a task")
        return context
