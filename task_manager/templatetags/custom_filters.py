from django import template
from django.conf import settings
from django.utils.translation import gettext as _

register = template.Library()


@register.filter
def format_title(value):
    default = str(settings.SITE_NAME)
    if value == default or not value:
        return default
    return _("TM: %(value)s") % {'value': value}
