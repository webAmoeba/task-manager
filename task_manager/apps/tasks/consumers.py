from channels.generic.websocket import AsyncJsonWebsocketConsumer


class TaskUpdatesConsumer(AsyncJsonWebsocketConsumer):
    group_name = "tasks_updates"

    async def connect(self):
        user = self.scope.get("user")
        if not user or user.is_anonymous:
            await self.close(code=4401)
            return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name, self.channel_name
        )

    async def task_update(self, event):
        await self.send_json(
            {
                "event": event.get("event", "updated"),
                "task": event.get("task"),
            }
        )

    async def task_delete(self, event):
        await self.send_json(
            {
                "event": event.get("event", "deleted"),
                "task": event.get("task"),
            }
        )
