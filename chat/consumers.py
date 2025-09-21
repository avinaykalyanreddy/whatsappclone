import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender_id = int(self.scope["url_route"]["kwargs"]["sender_id"])
        self.receiver_id = int(self.scope["url_route"]["kwargs"]["receiver_id"])

        ids = sorted([self.sender_id, self.receiver_id])
        self.room_group_name = f"chat_{ids[0]}_{ids[1]}"

        # Join the group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Fetch old messages
        messages_obj = await self.get_messages(self.sender_id, self.receiver_id)

        await self.accept()

        # Send old messages
        for message_obj in messages_obj:
            await self.send(text_data=json.dumps({
                "type": "previous_message",
                "sender": message_obj.sender_id,
                "message": message_obj.content,
                "created_at": message_obj.created_at.isoformat()
            }))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        # Save message safely
        msg = await self.save_message(self.sender_id, self.receiver_id, message)

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "sender": msg.sender_id,
                "message": msg.content,
                "created_at": msg.created_at.isoformat()
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": event["type"],
            "sender": event["sender"],
            "message": event["message"],
            "created_at": event["created_at"]
        }))

    # ---------------- ORM HELPERS ----------------
    @database_sync_to_async
    def get_messages(self, sender_id, receiver_id):
        from users.models import Messages
        return list(
            Messages.objects.filter(
                sender_id__in=[sender_id, receiver_id],
                receiver_id__in=[sender_id, receiver_id]
            ).order_by("created_at")
        )

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        from users.models import Messages
        return Messages.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content
        )
