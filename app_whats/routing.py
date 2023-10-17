from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/conversa/(?P<numero_telefone>\w+)/$', consumers.ReceberMensagemConsumer.as_asgi()),
]