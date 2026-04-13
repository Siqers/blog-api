import logging
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

# Retries важны для уведомлений — если Redis недоступен или БД упала,
# задача должна повториться чтобы пользователь не потерял уведомление
@shared_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_new_comment(comment_id):
    from apps.blog.models import Comment
    from apps.notifications.models import Notification

    comment = Comment.objects.select_related('author', 'post__author').get(id=comment_id)
    post = comment.post

    if comment.author != post.author:
        Notification.objects.create(
            recipient=post.author,
            comment=comment,
        )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'post_{post.slug}',
        {
            'type': 'comment_message',
            'message': {
                'comment_id': comment.id,
                'author': {'id': comment.author.id, 'email': comment.author.email},
                'body': comment.body,
                'created_at': comment.created_at.isoformat(),
            }
        }
    )

@shared_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def clear_expired_notifications():
    from apps.notifications.models import Notification
    from django.utils import timezone
    from datetime import timedelta
    deleted, _ = Notification.objects.filter(
        created_at__lt=timezone.now() - timedelta(days=30)
    ).delete()
    logger.info(f'Deleted {deleted} expired notifications')

@shared_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def generate_daily_stats():
    from apps.blog.models import Post, Comment
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from datetime import timedelta
    User = get_user_model()
    since = timezone.now() - timedelta(hours=24)
    posts = Post.objects.filter(created_at__gte=since).count()
    comments = Comment.objects.filter(created_at__gte=since).count()
    users = User.objects.filter(date_joined__gte=since).count()
    logger.info(f'Daily stats — posts: {posts}, comments: {comments}, users: {users}')