from django.urls import path
from .views import *

urlpatterns = [
    path('payment/', payment, name='payment'),
    path('process_payment/', process_payment, name='process_payment'),
    path('process_payment_pix/', process_payment_pix, name='process_payment_pix'),
    path('notifications_payments/', notifications_payments, name= 'notifications_payments'),
    path('endpoints_api/', endpoints_api, name='endpoints_api'),
    path('dados_ausentes', dados_ausentes, name='dados_ausentes'),
    path('verificar_dados_ausentes/', verificar_dados_ausentes, name='verificar_dados_ausentes'),
    path('pagamento_concluido/', pagamento_feito, name='pagamento_feito'),
]