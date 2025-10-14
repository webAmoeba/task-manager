from django.contrib import admin

from task_manager.apps.telegram.models import BotToken, TelegramProfile


@admin.register(BotToken)
class BotTokenAdmin(admin.ModelAdmin):
    list_display = ("token", "user", "is_active", "created_at", "expires_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("token", "user__username")
    autocomplete_fields = ("user",)


@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "chat_id",
        "username",
        "is_active",
        "linked_at",
        "last_interaction_at",
    )
    list_filter = ("is_active", "linked_at")
    search_fields = ("user__username", "chat_id", "username")
    autocomplete_fields = ("user",)
