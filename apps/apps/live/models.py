from django.db import models
from apps.accounts.models import User
from django.utils import timezone
import secrets

class LiveStream(models.Model):
    STATUS_CHOICES = [('starting', 'Starting'), ('live', 'Live'), ('ended', 'Ended'), ('failed', 'Failed')]
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_streams')
    title = models.CharField(max_length=150)
    stream_key = models.CharField(max_length=64, unique=True, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='starting')
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='live/thumbs/', null=True, blank=True)
    playlist_url = models.URLField(max_length=500, blank=True)
    viewer_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.stream_key:
            self.stream_key = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

class LiveReactionType(models.Model):
    code = models.CharField(max_length=20, unique=True)
    emoji = models.CharField(max_length=5)
    icon = models.ImageField(upload_to='live/reactions/')
    lottie = models.FileField(upload_to='live/reactions/lottie/', null=True, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

class LiveReaction(models.Model):
    stream = models.ForeignKey(LiveStream, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.ForeignKey(LiveReactionType, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['stream', 'sent_at'])]