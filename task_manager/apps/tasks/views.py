from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from task_manager.apps.labels.models import Label
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
        queryset = Task.objects.select_related(
            "status", "author", "executor"
        ).prefetch_related("labels")
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
        context["labels"] = Label.objects.all()
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
        context["labels"] = Label.objects.all()
        return context


class TaskUpdateView(CustomLoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        messages.success(self.request, _("Task successfully updated"))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("task_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Edit task")
        context["is_create_view"] = False
        context["statuses"] = Status.objects.all()
        context["executors"] = User.objects.all()
        context["labels"] = Label.objects.all()
        return context


class TaskDeleteView(CustomLoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Task
    template_name = "tasks/task_delete.html"
    success_url = reverse_lazy("task_list")
    success_message = _("Task successfully deleted")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            messages.error(
                request, _("A task can only be deleted by its author")
            )
            return HttpResponseForbidden(_("Forbidden"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Deleting a task")
        return context


class TaskCompleteView(CustomLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        task = get_object_or_404(
            Task.objects.select_related("executor", "author"), pk=kwargs["pk"]
        )
        if task.completed_at:
            messages.info(request, _("Task is already completed"))
            return redirect("task_detail", pk=task.pk)

        if request.user not in {task.author, task.executor}:
            messages.error(
                request, _("You do not have permission to complete this task.")
            )
            return HttpResponseForbidden(_("Forbidden"))

        task.completed_at = timezone.now()
        task.save(update_fields=["completed_at"])
        messages.success(request, _("Task marked as completed"))
        return redirect("task_detail", pk=task.pk)


class TaskDetailView(DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("View task")
        return context
