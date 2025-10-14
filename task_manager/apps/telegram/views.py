from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from task_manager.apps.telegram.models import BotToken, TelegramProfile


class TelegramSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "telegram/settings.html"
    success_url = reverse_lazy("telegram:settings")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["active_token"] = BotToken.objects.filter(
            user=user, is_active=True
        ).first()
        context["profile"] = TelegramProfile.objects.filter(user=user).first()
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        user = request.user

        if action == "generate_token":
            BotToken.create_for_user(user)
            messages.success(
                request,
                _(
                    "New bot token generated. \
                        Send it to the Telegram bot within 24 hours."
                ),
            )
        elif action == "revoke_token":
            BotToken.objects.filter(user=user, is_active=True).update(
                is_active=False
            )
            messages.info(request, _("Active token revoked."))
        elif action == "unlink":
            profile = TelegramProfile.objects.filter(user=user).first()
            if profile:
                profile.unlink()
                messages.info(request, _("Telegram account unlinked."))
            else:
                messages.warning(request, _("No Telegram account linked."))
        else:
            messages.error(request, _("Unknown action."))

        return redirect(self.success_url)
