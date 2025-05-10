from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.views.generic import ListView


class UserListView(ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        # Исключаем суперпользователей, включая admin
        return User.objects.filter(is_superuser=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Users")
        return context
