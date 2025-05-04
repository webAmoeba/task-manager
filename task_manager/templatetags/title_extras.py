from django import template

register = template.Library()


@register.filter
def format_title(value, default="Менеджер задач"):
    if value == default or not value:
        return default
    return f"МЗ: {value}"
