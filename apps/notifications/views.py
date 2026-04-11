import json
import asyncio
import redis.asyncio as aioredis
from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Notification
from . import serializers

class NotificationCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient = request.user, is_read = False
        ) .count()
        return Response({'unread_count': count})
class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(recipient = request.user)
        paginator = PageNumberPagination() 
        paginator.page_size = 10
        page = paginator.paginate_queryset(notifications, request)
        from .serializers import NotificationSerializer
        serializers = NotificationSerializer(page, many = True)
        return paginator .get_paginated_response(serializer.data)
       
class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request): 
        Notification.objects.filter(
            recipient = request.user, is_read = False
        ) .update(is_read = True)
        return Response({'status': 'ok'})
    
async def post_stream(request):
    async def event_stream():
        r = await aioredis.from_url(settings.REDIS_URL)
        pubsub = r.pubsub()
        await pubsub.subscribe('post_published')
        try: 
            async for massage in pubsub.listen():
                if massage['type'] == 'massage':
                    yield f"data: {massage['data'].decode()} \n\n"
        finally:
            await pubsub.unsubscribe('post_published')
            await r.close()
    return StreamingHttpResponse(event_stream(), content_type= 'text/event-stream')
                    
