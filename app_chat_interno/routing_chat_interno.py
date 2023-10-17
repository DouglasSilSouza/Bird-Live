from django.urls import re_path
from . import consumers_chat_interno

websocket_urlpatterns = [
    re_path(r'ws/socket-server/', consumers_chat_interno.ChatConsumer.as_asgi())
]