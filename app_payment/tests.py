#from django.test import TestCase
from ecommerce_cart.models import ItemCarrinho

def teste():
    items = ItemCarrinho.objects.all()
    itens = []
    for i in items:
        itens.append({"titulo": i.title, "quantidade": i.quantidade, "valor_unitario": i.valor_unitario})
    return itens

print(teste())