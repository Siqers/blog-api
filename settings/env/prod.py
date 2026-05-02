# settings/env/prod.py
from ..base import *

DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@blog-api.com'

CSRF_TRUSTED_ORIGINS = ['http://localhost']