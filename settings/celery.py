import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.env.local')

app = Celery('blog')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'publish-scheduled-posts': {
        'task': 'apps.blog.tasks.publish_scheduled_posts',
        'schedule': 60.0,  # каждую минуту
    },
    'clear-expired-notifications': {
        'task': 'apps.notifications.tasks.clear_expired_notifications',
        'schedule': crontab(hour=3, minute=0),  # каждый день в 03:00
    },
    'generate-daily-stats': {
        'task': 'apps.notifications.tasks.generate_daily_stats',
        'schedule': crontab(hour=0, minute=0),  # каждый день в 00:00
    },
}