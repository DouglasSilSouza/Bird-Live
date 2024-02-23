import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from ..app_payment.routing import websocket_urlpatterns as app_payment_urlpatterns

websocket_router = URLRouter([
    *app_payment_urlpatterns,
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
