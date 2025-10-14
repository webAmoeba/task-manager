"""Telegram bot entrypoint using aiogram."""

import asyncio
import logging
import os

import django
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")
django.setup()

from django.conf import settings  # noqa: E402
from django.utils import timezone  # noqa: E402

from task_manager.apps.notifications.models import Notification  # noqa: E402
from task_manager.apps.tasks.models import Task  # noqa: E402
from task_manager.apps.telegram.models import (  # noqa: E402
    BotToken,
    TelegramProfile,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()


def _get_profile(message: Message) -> TelegramProfile | None:
    chat_id = message.chat.id
    profile = (
        TelegramProfile.objects.filter(chat_id=chat_id, is_active=True)
        .select_related("user")
        .first()
    )
    if profile:
        profile.username = message.chat.username or ""
        profile.first_name = message.chat.first_name or ""
        profile.last_name = message.chat.last_name or ""
        profile.touch()
    return profile


async def _link_account(message: Message, token_value: str):
    token = (
        BotToken.objects.select_related("user")
        .filter(token=token_value.strip(), is_active=True)
        .first()
    )
    if not token:
        await message.answer(
            "❌ Invalid or expired token. Generate a new one in the web \
                application."
        )
        return

    user = token.user
    profile, _ = TelegramProfile.objects.get_or_create(user=user)
    profile.chat_id = message.chat.id
    profile.username = message.chat.username or ""
    profile.first_name = message.chat.first_name or ""
    profile.last_name = message.chat.last_name or ""
    profile.is_active = True
    profile.last_interaction_at = timezone.now()
    profile.save()

    token.is_active = False
    token.save(update_fields=["is_active"])

    await message.answer(
        "✅ Linked successfully! You will now receive notifications.\n"
        "Use /tasks to view assigned tasks."
    )


@dp.message(Command("start"))
async def cmd_start(message: Message):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) > 1:
        await _link_account(message, parts[1])
    else:
        await message.answer(
            "👋 Hello! Send me your bot token to link your account.\n"
            "You can obtain it in the web application under Telegram settings."
        )


@dp.message()
async def handle_plain_text(message: Message):
    text = (message.text or "").strip()
    if len(text) >= 16:  # looks like token
        await _link_account(message, text)
    else:
        await message.answer(
            "Send /tasks to list your tasks or provide a valid token."
        )


async def _format_task(task: Task) -> str:
    status = (
        "✅"
        if task.completed_at
        else "⚠️"
        if getattr(task, "is_overdue", False)
        else "📝"
    )
    due = task.due_at.strftime("%d.%m %H:%M") + " UTC" if task.due_at else "—"
    return f"{status} <b>{task.id}</b> — {task.name}\nDue: {due}"


@dp.message(Command("tasks"))
async def cmd_tasks(message: Message):
    profile = _get_profile(message)
    if not profile:
        await message.answer(
            "Please link your account first by sending the token."
        )
        return

    tasks = (
        Task.objects.select_related("status")
        .filter(executor=profile.user)
        .order_by("completed_at__isnull", "due_at")
    )

    if not tasks.exists():
        await message.answer("🎉 No tasks assigned to you.")
        return

    lines = [await _format_task(task) for task in tasks[:10]]
    if tasks.count() > 10:
        lines.append("…")
    await message.answer("\n\n".join(lines))


@dp.message(Command("notifications"))
async def cmd_notifications(message: Message):
    profile = _get_profile(message)
    if not profile:
        await message.answer("Please link your account first.")
        return

    notifications = Notification.objects.filter(
        user=profile.user,
        is_read=False,
    ).order_by("-created_at")[:10]

    if not notifications:
        await message.answer("📭 No unread notifications.")
        return

    lines = []
    for notif in notifications:
        line = f"🔔 <b>{notif.title}</b>"
        if notif.message:
            line += f"\n{notif.message}"
        lines.append(line)
    await message.answer("\n\n".join(lines))


@dp.message(Command("complete"))
async def cmd_complete(message: Message):
    profile = _get_profile(message)
    if not profile:
        await message.answer("Please link your account first.")
        return

    parts = (message.text or "").split(maxsplit=1)
    args = parts[1] if len(parts) > 1 else ""
    if not args.isdigit():
        await message.answer("Usage: /complete <task_id>")
        return

    task_id = int(args)
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        await message.answer("Task not found.")
        return

    user = profile.user
    if task.executor != user and task.author != user:
        await message.answer("You don't have permission to complete this task.")
        return

    if task.completed_at:
        await message.answer("Task is already completed.")
        return

    task.completed_at = timezone.now()
    task.save(update_fields=["completed_at"])
    await message.answer("✅ Task marked as completed.")


async def main():
    logger.info("Starting Telegram bot")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
