import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.group_name = f'post_{self.slug}'

        # JWT auth via query param
        token = self.scope['query_string'].decode().split('token=')[-1]
        user = await self.get_user(token)
        if not user:
            await self.close(code=4001)
            return

        # Check post exists
        post_exists = await self.check_post(self.slug)
        if not post_exists:
            await self.close(code=4004)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def comment_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def get_user(self, token):
        try:
            data = AccessToken(token)
            return User.objects.get(id=data['user_id'])
        except Exception:
            return None

    @database_sync_to_async
    def check_post(self, slug):
        from apps.blog.models import Post
        return Post.objects.filter(slug=slug).exists()
