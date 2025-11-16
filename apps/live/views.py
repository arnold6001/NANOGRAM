from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import LiveStream
from .tasks import transcode_to_hls
from .serializers import StartLiveSerializer, LiveStreamSerializer

class StartLiveView(APIView):
    def post(self, request):
        serializer = StartLiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stream = LiveStream.objects.create(host=request.user, title=serializer.validated_data['title'])
        rtmp_url = f"rtmp://your-domain.com/live/live_{stream.stream_key}"
        return Response({'stream_id': stream.id, 'rtmp_url': rtmp_url, 'stream_key': stream.stream_key})

class IngestVerifyView(APIView):
    authentication_classes = []; permission_classes = []
    def post(self, request):
        name = request.data.get('name', '').split('_')[-1]
        if LiveStream.objects.filter(stream_key=name, status='starting').exists():
            return Response({'call': 'publish', 'code': 200})
        return Response({'code': 403}, status=403)

class IngestDoneView(APIView):
    def post(self, request):
        name = request.data.get('name', '').split('_')[-1]
        try:
            stream = LiveStream.objects.get(stream_key=name)
            stream.status = 'ended'; stream.ended_at = timezone.now(); stream.save()
        except: pass
        return Response(status=200)