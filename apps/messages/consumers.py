# apps/messages/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Message

class DMConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = f"dm_{self.scope['url_route']['kwargs']['chat_id']}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg = await sync_to_async(Message.objects.create)(
            chat_id=self.scope['url_route']['kwargs']['chat_id'],
            sender=self.scope["user"],
            text=data['text'],
        )
        await self.channel_layer.group_send(
            self.room_name,
            {"type": "chat_message", "message": msg.text, "sender": msg.sender.username}
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))