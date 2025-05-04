from django import template
from django.utils.translation import gettext as _

register = template.Library()

@register.filter
def format_title(value, default=_("Task manager")):
    if value == default or not value:
        return default
    return _("TM: %(value)s") % {'value': value}
