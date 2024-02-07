from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('pagamentos/', admin_carts, name='pagamentos'),
    path('pagamento/<int:id>', admin_payments, name='pagamento'),
]