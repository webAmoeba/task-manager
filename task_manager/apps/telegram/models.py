from __future__ import annotations

import secrets

from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone

User = get_user_model()


def generate_token() -> str:
    # 32 bytes -> 43 urlsafe characters
    return secrets.token_urlsafe(32)


class BotToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="telegram_bot_tokens",
    )
    token = models.CharField(
        max_length=96,
        unique=True,
        validators=[MinLengthValidator(16)],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Token for {self.user}"

    def deactivate(self):
        if self.is_active:
            self.is_active = False
            self.save(update_fields=["is_active"])

    @classmethod
    def create_for_user(cls, user: User) -> "BotToken":
        cls.objects.filter(user=user, is_active=True).update(is_active=False)
        return cls.objects.create(user=user, token=generate_token())


class TelegramProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="telegram_profile",
    )
    chat_id = models.BigIntegerField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    linked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_interaction_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Telegram account"
        verbose_name_plural = "Telegram accounts"

    def __str__(self) -> str:
        return f"{self.user} ↔ {self.chat_id}"

    def touch(self):
        self.last_interaction_at = timezone.now()
        self.save(update_fields=["last_interaction_at"])

    def unlink(self):
        self.is_active = False
        self.chat_id = None
        self.username = ""
        self.first_name = ""
        self.last_name = ""
        self.save(update_fields=[
            "is_active",
            "chat_id",
            "username",
            "first_name",
            "last_name",
        ])
