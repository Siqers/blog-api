from functools import wraps
import redis
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status

# connection to redis
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def rate_limit(key_prefix: str, max_requests: int, window_seconds: int):
    """
    Decorator for limiting the number of requests

    :param key_prefix: Redis key prefix (e.g., 'register')
    :param max_requests: Maximum number of requests
    :param window_seconds: Time window in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if hasattr(arg, 'META'):
                    request = arg
                    break
            
            if request is None:
                request = kwargs.get('request')

            if request:
                if hasattr(request.user, 'id') and request.user.is_authenticated:
                    identifier = f'user_{request.user.id}'
                else:
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        ip = x_forwarded_for.split(',')[0]
                    else:
                        ip = request.META.get('REMOTE_ADDR')
                    identifier = f'ip_{ip}'
                
                redis_key = f'ratelimit:{key_prefix}:{identifier}'
                current = redis_client.get(redis_key)

                if current is None:
                    redis_client.setex(redis_key, window_seconds, 1)
                elif int(current) >= max_requests:
                    return Response(
                        {'detail': 'Too many requests. Try again later.'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )
                else:
                    redis_client.incr(redis_key)

            return view_func(*args, **kwargs)
        return wrapper
    return decorator