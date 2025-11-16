from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    totp_secret = models.CharField(max_length=32, blank=True)
    email_verified = models.BooleanField(default=False)
    fcm_token = models.CharField(max_length=255, blank=True)