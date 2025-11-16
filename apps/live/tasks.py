from celery import shared_task
import ffmpeg, os, shutil, time
from django.conf import settings
from .models import LiveStream

@shared_task(bind=True)
def transcode_to_hls(self, rtmp_url, stream_id):
    stream = LiveStream.objects.get(id=stream_id)
    output_dir = os.path.join(settings.MEDIA_ROOT, 'live', str(stream.id))
    os.makedirs(output_dir, exist_ok=True)
    playlist = os.path.join(output_dir, 'index.m3u8')
    try:
        ffmpeg.input(rtmp_url).output(playlist, f='hls', hls_time=4, hls_list_size=0, preset='veryfast').run(overwrite_output=True)
        from core.storages.media_cdn import CDNBucketStorage
        storage = CDNBucketStorage()
        for root, _, files in os.walk(output_dir):
            for f in files:
                path = os.path.join(root, f)
                with open(path, 'rb') as data:
                    rel = os.path.relpath(path, settings.MEDIA_ROOT)
                    storage.save(rel, data)
        stream.playlist_url = storage.url(f'live/{stream.id}/index.m3u8')
        stream.status = 'live'; stream.started_at = timezone.now(); stream.save()
    except Exception as e:
        stream.status = 'failed'; stream.save(); raise self.retry(exc=e)

@shared_task
def cleanup_hls(stream_id):
    time.sleep(3600)
    path = os.path.join(settings.MEDIA_ROOT, 'live', str(stream_id))
    if os.path.isdir(path): shutil.rmtree(path)