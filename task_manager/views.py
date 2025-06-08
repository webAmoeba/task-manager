from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def custom_404(request, exception):
    return render(
        request,
        "404.html",
        context={"page_title": _("Page not found")},
        status=404,
    )


def index(request):
    return render(
        request,
        "index.html",
    )
