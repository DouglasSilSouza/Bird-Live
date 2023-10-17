from ecommerce_cart.models import Carrinho
from django.test import TestCase


cart = Carrinho.objects.count()
print(cart)

