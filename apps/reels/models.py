# apps/reels/models.py
class Reel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.FileField(upload_to='reels/', validators=[FileExtensionValidator(['mp4'])])
    thumbnail = models.ImageField(upload_to='reels/thumbs/')
    caption = models.CharField(max_length=2200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveBigIntegerField(default=0)

# Signal to generate thumbnail with ffmpeg
@receiver(post_save, sender=Reel)
def generate_reel_thumbnail(sender, instance, created, **kwargs):
    if created:
        from services.media.thumbnail import make_thumbnail
        make_thumbnail(instance.video.path, instance.thumbnail.path)