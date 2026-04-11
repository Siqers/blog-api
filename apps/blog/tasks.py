import logging
from celery import shared_task
from django.conf import settings 
logger = logging.getLogger(__name__)

@shared_task(autoretry_for = (Exception,), retry_backoff = True, max_retries = 3)
def publish_scheduled_posts():
    from django.utils import timezone
    from apps.blog.models import Post
    import redis
    import json
    
    now = timezone.now()
    posts = Post.objects.filter(status = 'scheduled', publish_at__lte = now)

    r = redis.from_url(settings.REDIS_URL)

    for post in posts:
        post.status = 'published'
        post.save()

        data = json.dumps({
            'post_id' : post.id,
            'title' : post.title,
            'slug' : post.slug,
            'author' : {'id' : post.author.id, 'email': post.email},
            'published_at' : post.published_at.isoformat() if post.published_at else None,
        })
        r.publish('post_published', data)
        logger.info(f'Published scheduled post: {post.slog}')




