from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DeleteView, ListView
from django.views.generic.edit import UpdateView

from task_manager.apps.statuses.models import Status
from task_manager.apps.tasks.forms import TaskForm
from task_manager.apps.tasks.models import Task

User = get_user_model()


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"
    template_name = "tasks/task_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Tasks")
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create task")
        context["is_create_view"] = True
        context["statuses"] = Status.objects.all()
        context["executors"] = User.objects.all()
        return context


class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("task_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Edit task")
        context["is_create_view"] = False
        context["statuses"] = context["form"].fields["status"].queryset
        context["executors"] = context["form"].fields["executor"].queryset
        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


# class TaskDeleteView(DeleteView):
#     model = Task
#     template_name = "tasks/task_delete.html"
#     success_url = reverse_lazy("task_list")

#     def dispatch(self, request, *args, **kwargs):
#         obj = self.get_object()
#         if obj.author != request.user:
#             raise PermissionDenied
#         return super().dispatch(request, *args, **kwargs)

#     def delete(self, request, *args, **kwargs):
#         obj = self.get_object()
#         success_url = self.get_success_url()
#         messages.success(self.request, _("asdf"))
#         obj.delete()
#         return HttpResponseRedirect(success_url)


#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["page_title"] = _("Deleting a task")
#         return context
class TaskDeleteView(SuccessMessageMixin, DeleteView):
    model = Task
    template_name = "tasks/task_delete.html"
    success_url = reverse_lazy("task_list")
    success_message = _("Task successfully deleted")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        messages.success(self.request, self.success_message)
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Deleting a task")
        return context
