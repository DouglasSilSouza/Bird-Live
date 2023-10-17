from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('webhook/', verify_webhook, name='webhook'),
    path('telegram_webhook/', telegram_webhook, name='telegram_webhook'),
    path('send_whatsapp_message/', send_whatsapp_message, name='send_whatsapp_message'),
    path('iniciar_chat/', iniciar_chat, name='iniciar_chat'),
    path('encerrar_atendimento/<int:numero>', encerrar_atendimento, name='encerrar_atendimento'),
    path('conversas_whatsapp', conversas_whatsapp, name='conversas_whatsapp'),
    path('historico/<int:id>', ver_histórico, name='historico'),
    path('chat_window', chat_window, name='chat_window'),
]