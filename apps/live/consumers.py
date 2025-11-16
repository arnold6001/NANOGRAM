import json, random, redis
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.cache import cache
from apps.live.models import LiveStream, LiveReaction, LiveReactionType
from core.storages.media_cdn import CDNBucketStorage

r = redis.Redis(host='redis', port=6379, db=0)
storage = CDNBucketStorage()
COOLDOWN_KEY = "reaction_cooldown:{user_id}:{stream_id}"

class LiveConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.stream_id = self.scope['url_route']['kwargs']['stream_id']
        self.room = f"live_{self.stream_id}"
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close(); return
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()
        await sync_to_async(r.incr)(f"viewers:{self.stream_id}")
        await self.update_viewer_count()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room, self.channel_name)
        await sync_to_async(r.decr)(f"viewers:{self.stream_id}")
        await self.update_viewer_count()

    async def receive_json(self, content):
        if content.get('type') == 'reaction':
            await self.handle_reaction(content)
        elif content.get('type') == 'chat':
            await self.channel_layer.group_send(self.room, {
                'type': 'chat_message',
                'username': self.user.username,
                'message': content['message'],
            })

    async def handle_reaction(self, content):
        code = content.get('reaction'); key = COOLDOWN_KEY.format(user_id=self.user.id, stream_id=self.stream_id)
        if cache.get(key, 0) >= 5:
            await self.send_json({"error": "Too many reactions"}); return
        cache.set(key, cache.get(key, 0) + 1, timeout=1)

        try:
            rt = await sync_to_async(LiveReactionType.objects.get)(code=code)
        except: return

        redis_key = f"live:reactions:{self.stream_id}:{code}"
        count = await sync_to_async(r.incr)(redis_key)
        await sync_to_async(LiveReaction.objects.create)(stream_id=self.stream_id, user=self.user, reaction_type=rt)

        lottie_url = storage.url(rt.lottie.name) if rt.lottie else None
        await self.channel_layer.group_send(self.room, {
            'type': 'reaction_animation',
            'reaction': code,
            'emoji': rt.emoji,
            'lottie_url': lottie_url,
            'count': count,
            'user': self.user.username,
            'x': random.uniform(0.1, 0.9),
        })

    async def update_viewer_count(self):
        count = int(await sync_to_async(r.get)(f"viewers:{self.stream_id}") or 0)
        await sync_to_async(LiveStream.objects.filter(id=self.stream_id).update)(viewer_count=count)
        await self.channel_layer.group_send(self.room, {'type': 'viewer_count', 'count': count})

    async def chat_message(self, event): await self.send_json(event)
    async def viewer_count(self, event): await self.send_json(event)
    async def reaction_animation(self, event): await self.send_json(event)