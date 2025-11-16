import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd-party
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'django_filters',
    'drf_yasg',
    'channels',
    'corsheaders',
    'storages',

    # Local
    'apps.accounts',
    'apps.posts',
    'apps.stories',
    'apps.reels',
    'apps.igtv',
    'apps.messages',
    'apps.hashtags',
    'apps.explore',
    'apps.notifications',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'core.middleware.ratelimit.RateLimitMiddleware',   # <-- our rate limiter
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# ---------- AUTH ----------
AUTH_USER_MODEL = 'accounts.User'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}

# ---------- MEDIA CDN ----------
DEFAULT_FILE_STORAGE = 'core.storages.media_cdn.CDNBucketStorage'
AWS_S3_REGION_NAME = config('AWS_REGION')
AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT')      # e.g. https://<id>.r2.cloudflarestorage.com
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_BUCKET')
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 3600

# ---------- CHANNELS ----------
ASGI_APPLICATION = 'core.asgi.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [(config('REDIS_HOST'), 6379)]},
    },
}

# ---------- PUSH ----------
FCM_API_KEY = config('FCM_API_KEY')
APNS_CERT = config('APNS_CERT_PATH', default=None)