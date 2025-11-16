from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
import time

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_ip(request)
        key = f"rl:{ip}"
        now = int(time.time())
        pipe = cache.client.get_client().pipeline()
        pipe.zremrangebyscore(key, '-inf', now - 60)
        pipe.zcard(key)
        pipe.zadd(key, {now: now})
        pipe.expire(key, 60)
        _, count, _, _ = pipe.execute()
        if count > 120:
            return JsonResponse({"detail": "Rate limit exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        return self.get_response(request)

    @staticmethod
    def get_ip(request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        return (xff.split(',')[0] if xff else request.META.get('REMOTE_ADDR', '')).strip()