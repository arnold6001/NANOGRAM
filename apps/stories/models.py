# apps/stories/models.py
from django.db import models
from apps.accounts.models import User

class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    media = models.FileField(upload_to='stories/')
    caption = models.CharField(max_length=2200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)   # auto-delete

    def save(self, *args, **kwargs):
        if not self.pk:
            from datetime import timedelta
            self.expires_at = self.created_at + timedelta(hours=24)
        super().save(*args, **kwargs)

# Auto-cleanup task (Celery beat)
@shared_task
def delete_expired_stories():
    Story.objects.filter(expires_at__lte=timezone.now()).delete()