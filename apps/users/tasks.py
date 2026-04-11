import logging
from celery import shared_task

logger = logging.getLogger(__name__)

# Retries важны для email — если SMTP сервер временно недоступен,
# пользователь не получит welcome email. Retry решает это автоматически.
@shared_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_welcome_email(user_id):
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail
    from django.conf import settings
    from django.template.loader import render_to_string
    from django.utils import translation

    User = get_user_model()
    user = User.objects.get(id=user_id)

    with translation.override(user.language):
        subject = render_to_string('emails/welcome/subject.txt', {'user': user}).strip()
        body = render_to_string('emails/welcome/body.txt', {'user': user})

        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        logger.info('Welcome email sent to %s', user.email)