import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from app_whats.routing import websocket_urlpatterns as app1_websocket_urlpatterns
from app_chat_interno.routing_chat_interno import websocket_urlpatterns as app2_websocket_urlpatterns

websocket_router = URLRouter([
    *app1_websocket_urlpatterns,
    *app2_websocket_urlpatterns,
])

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dls_empresa.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
                websocket_router
        )
    ),
})
