from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from task_manager.apps.tasks.models import Task


def custom_404(request, exception):
    return render(
        request,
        "404.html",
        context={"page_title": _("Page not found")},
        status=404,
    )


def index(request):
    today = timezone.localdate()
    now = timezone.now()

    created_today_qs = Task.objects.select_related("status").filter(
        created_at__date=today
    )
    completed_today_qs = Task.objects.select_related("status").filter(
        completed_at__date=today
    )
    overdue_qs = Task.objects.select_related("status").filter(
        due_at__isnull=False, due_at__lt=now, completed_at__isnull=True
    )

    context = {
        "page_title": _("Dashboard"),
        "stats": {
            "created_today": created_today_qs.count(),
            "completed_today": completed_today_qs.count(),
            "overdue_now": overdue_qs.count(),
        },
        "created_today_list": list(
            created_today_qs.order_by("-created_at")[:5]
        ),
        "completed_today_list": list(
            completed_today_qs.order_by("-completed_at")[:5]
        ),
        "overdue_list": list(overdue_qs.order_by("due_at")[:5]),
    }

    return render(request, "index.html", context)
