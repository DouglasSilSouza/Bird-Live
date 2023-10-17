from .products.getproducts import GetProducts
from app_authentication.models import Cadastro
from ecommerce_cart.models import Carrinho, ItemCarrinho
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Sum
import asyncio

# Create your views here.
async def base(request):
        try:
            user = await asyncio.get_event_loop().run_in_executor(None, lambda: Cadastro.objects.get(pk=request.user.id))
            cart = await asyncio.get_event_loop().run_in_executor(None, lambda: Carrinho.objects.get(usuario=user))
            itens = await asyncio.get_event_loop().run_in_executor(None, lambda: ItemCarrinho.objects.filter(carrinho=cart).aggregate(soma=Sum('quantidade')))
            quantidade = itens['soma']
            return JsonResponse({"quantity": quantidade})
        except Carrinho.DoesNotExist:
            return JsonResponse({"quantity": 0})

def home(request):
    data = GetProducts().get_products()
    return render(request, "ecommerce_main/e-main.html", {"data": data})

def productOnly(request, id):
    data = GetProducts(id).get_products()
    return render(request, "ecommerce_main/e-product_only.html", {"data": data})