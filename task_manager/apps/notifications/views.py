from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView

from task_manager.apps.notifications.models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    template_name = "notifications/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Notification.objects.filter(user=self.request.user)
            .select_related("task")
            .order_by("-created_at")
        )
        status_filter = self.request.GET.get("status")
        if status_filter == "unread":
            queryset = queryset.filter(is_read=False)
        elif status_filter == "read":
            queryset = queryset.filter(is_read=True)
        return queryset


class NotificationToggleReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        notification = get_object_or_404(
            Notification, pk=kwargs["pk"], user=request.user
        )
        action = request.POST.get("action")

        if action == "mark_read" and not notification.is_read:
            notification.mark_read()
            messages.success(request, _("Notification marked as read."))
        elif action == "mark_unread" and notification.is_read:
            notification.is_read = False
            notification.read_at = None
            notification.save(update_fields=["is_read", "read_at"])
            messages.info(request, _("Notification marked as unread."))

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("notifications:list")
