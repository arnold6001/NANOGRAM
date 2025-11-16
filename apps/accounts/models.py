# apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    totp_secret = models.CharField(max_length=32, blank=True)  # pyotp
    email_verified = models.BooleanField(default=False)

# apps/accounts/auth.py
import pyotp, uuid
from django.core.mail import send_mail
from django.utils import timezone

def send_verification_email(user):
    token = uuid.uuid4().hex
    VerificationToken.objects.update_or_create(
        user=user, defaults={'token': token, 'expires_at': timezone.now() + timezone.timedelta(hours=1)}
    )
    url = f"https://api.yourapp.com/verify-email/{token}/"
    send_mail(
        "Verify your email",
        f"Click: {url}",
        "no-reply@yourapp.com",
        [user.email],
    )

def enable_2fa(user):
    secret = pyotp.random_base32()
    user.totp_secret = secret
    user.save()
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=user.email, issuer_name="YourApp")
    return provisioning_uri