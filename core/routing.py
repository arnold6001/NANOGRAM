from django.urls import path
from apps.live.consumers import LiveConsumer

websocket_urlpatterns = [
    path("ws/live/<int:stream_id>/", LiveConsumer.as_asgi()),
]