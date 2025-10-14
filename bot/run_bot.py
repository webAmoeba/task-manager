"""Telegram bot entrypoint using aiogram."""

import asyncio
import logging
import os

import django
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message
from asgiref.sync import sync_to_async

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")
django.setup()

from django.conf import settings  # noqa: E402
from django.db.models import F  # noqa: E402
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

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()


def _get_profile_sync(
    chat_id: int, username: str, first_name: str, last_name: str
):
    profile = (
        TelegramProfile.objects.filter(chat_id=chat_id, is_active=True)
        .select_related("user")
        .first()
    )
    if profile:
        profile.username = username or ""
        profile.first_name = first_name or ""
        profile.last_name = last_name or ""
        profile.last_interaction_at = timezone.now()
        profile.save(
            update_fields=[
                "username",
                "first_name",
                "last_name",
                "last_interaction_at",
            ]
        )
    return profile


def _link_account_sync(
    token_value: str,
    chat_id: int,
    username: str,
    first_name: str,
    last_name: str,
):
    token = (
        BotToken.objects.select_related("user")
        .filter(token=token_value.strip(), is_active=True)
        .first()
    )
    if not token:
        return None

    user = token.user
    profile, _ = TelegramProfile.objects.get_or_create(user=user)
    profile.chat_id = chat_id
    profile.username = username or ""
    profile.first_name = first_name or ""
    profile.last_name = last_name or ""
    profile.is_active = True
    profile.last_interaction_at = timezone.now()
    profile.save()

    token.is_active = False
    token.save(update_fields=["is_active"])

    return profile


async def _get_profile(message: Message) -> TelegramProfile | None:
    return await sync_to_async(
        _get_profile_sync,
        thread_sensitive=True,
    )(
        message.chat.id,
        message.chat.username or "",
        message.chat.first_name or "",
        message.chat.last_name or "",
    )


async def _link_account(message: Message, token_value: str):
    profile = await sync_to_async(
        _link_account_sync,
        thread_sensitive=True,
    )(
        token_value,
        message.chat.id,
        message.chat.username or "",
        message.chat.first_name or "",
        message.chat.last_name or "",
    )
    if not profile:
        await message.answer(
            "❌ Invalid or expired token. \
                Generate a new one in the web application."
        )
        return

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


def _fetch_tasks_for_user(user_id: int):
    queryset = (
        Task.objects.select_related("status")
        .filter(executor_id=user_id)
        .order_by(F("completed_at").asc(nulls_last=True), F("due_at").asc(nulls_last=True))
    )
    return list(queryset)


def _fetch_notifications(user_id: int):
    queryset = Notification.objects.filter(
        user_id=user_id, is_read=False
    ).order_by("-created_at")[:10]
    return list(queryset)


def _complete_task_sync(task_id: int, user_id: int) -> str:
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return "not_found"

    if task.executor_id != user_id and task.author_id != user_id:
        return "forbidden"

    if task.completed_at:
        return "already"

    task.completed_at = timezone.now()
    task.save(update_fields=["completed_at"])
    return "ok"


@dp.message(Command("tasks"))
async def cmd_tasks(message: Message):
    profile = await _get_profile(message)
    if not profile:
        await message.answer(
            "Please link your account first by sending the token."
        )
        return

    tasks = await sync_to_async(_fetch_tasks_for_user, thread_sensitive=True)(
        profile.user_id
    )

    if not tasks:
        await message.answer("🎉 No tasks assigned to you.")
        return

    lines = [await _format_task(task) for task in tasks[:10]]
    if len(tasks) > 10:
        lines.append("…")
    await message.answer("\n\n".join(lines))


@dp.message(Command("notifications"))
async def cmd_notifications(message: Message):
    profile = await _get_profile(message)
    if not profile:
        await message.answer("Please link your account first.")
        return

    notifications = await sync_to_async(
        _fetch_notifications, thread_sensitive=True
    )(profile.user_id)

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
    profile = await _get_profile(message)
    if not profile:
        await message.answer("Please link your account first.")
        return

    parts = (message.text or "").split(maxsplit=1)
    args = parts[1] if len(parts) > 1 else ""
    if not args.isdigit():
        await message.answer("Usage: /complete <task_id>")
        return

    task_id = int(args)
    result = await sync_to_async(_complete_task_sync, thread_sensitive=True)(
        task_id, profile.user_id
    )

    messages_map = {
        "ok": "✅ Task marked as completed.",
        "not_found": "Task not found.",
        "forbidden": "You don't have permission to complete this task.",
        "already": "Task is already completed.",
    }
    await message.answer(messages_map.get(result, "Something went wrong."))


@dp.message()
async def handle_plain_text(message: Message):
    text = (message.text or "").strip()
    if text.startswith("/"):
        return
    if len(text) >= 16:
        await _link_account(message, text)
    else:
        await message.answer(
            "Send /tasks to list your tasks or provide a valid token."
        )


async def main():
    logger.info("Starting Telegram bot")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
