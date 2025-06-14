from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from task_manager.apps.users.forms import (
    CustomUserChangeForm,
    CustomUserCreationForm,
)


class CustomLoginView(LoginView):
    def form_valid(self, form):
        messages.success(self.request, _("You are logged in"))
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, _("You are logged out"))
        return super().dispatch(request, *args, **kwargs)


class UserListView(ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"

    # def get_queryset(self):
    #     # Исключаем суперпользователей, включая admin
    #     return User.objects.filter(is_superuser=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Users")
        return context


class UserCreateView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("User successfully registered"))
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Registration")
        context["is_create_view"] = True
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("user_list")

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user != user:
            messages.error(
                request, _("You do not have permission to change another user.")
            )
            return redirect("user_list")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _("User successfully updated"))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Update user")
        context["is_create_view"] = False
        return context


class UserDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = User
    template_name = "users/user_delete.html"
    success_url = reverse_lazy("user_list")
    success_message = _("User successfully deleted")

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user != user:
            messages.error(
                request, _("You do not have permission to change another user.")
            )
            return redirect("user_list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.get_object()
        from task_manager.apps.tasks.models import Task

        tasks_in_use = Task.objects.filter(
            Q(author=user) | Q(executor=user)
        ).exists()

        if tasks_in_use:
            messages.error(
                self.request, _("Cannot delete user because it is in use")
            )
            return redirect("user_list")

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Deleting a user")
        return context
