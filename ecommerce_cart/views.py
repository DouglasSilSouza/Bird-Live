from .login_required_message import login_required_message_and_redirect
from ecommerce_main.products.getproducts import GetProducts
from app_authentication.models import Cadastro
from ecommerce_cart.models import Carrinho, ItemCarrinho
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
import traceback
import json

# Create your views here.
@login_required_message_and_redirect(login_url='login_view')
def carrinho(request):
    item = ""
    try:
        user = Cadastro.objects.get(pk = request.user.id)
        cart = Carrinho.objects.get(usuario=user)
        item = ItemCarrinho.objects.filter(carrinho=cart)
    except Carrinho.DoesNotExist:
        print("Carrinho não encontrado")
    except Carrinho.MultipleObjectsReturned:
        print("Múltiplos carrinhos encontrados")
    return render(request, "ecommerce_cart/e-cart.html", {"carrinho": item})

def getdatacart(request):
    body = json.loads(request.body)
    try:
        user = Cadastro.objects.get(pk = request.user.id)
        cart, _ = Carrinho.objects.get_or_create(usuario = user)
        id_product = int(body.get('idProduct'))
        products = GetProducts(id_product).get_products()

        subtotal = products.get('price') * int(body.get('qtd'))

        item_cart, created = ItemCarrinho.objects.get_or_create(produto_id = id_product, 
            defaults={
                "carrinho": cart,
                "quantidade": int(body.get('qtd')),
                "title": products.get('title'),
                "description": products.get('description'),
                "image_url": products.get('image'),
                "valor_unitario": float(products.get('price')),
                "subtotal": float(subtotal),
            })
        
        if not created:
            quantity = item_cart.quantidade
            qtd = int(body.get('qtd'))
            soma = qtd + quantity
            item_cart.quantidade = soma
            item_cart.save()

        return JsonResponse({"status": 'OK', "message": "Adicionado ao carinho com sucesso!"})
    except Exception as e:
        print(e)
        traceback_str = traceback.format_exc()
        print(f"Erro: {traceback_str}")
        return JsonResponse({"status": 'error', "message": "Erro ao salvar o carrinho!"})

@login_required_message_and_redirect(login_url='login_view')
@csrf_exempt
def deletdatacart(request):
    body = json.loads(request.body)
    try:
        id_product = int(body.get('idProduct'))
        item_cart = ItemCarrinho.objects.filter(produto_id = id_product).first()
        if item_cart is not None:
            item_cart.delete()
            return JsonResponse({"status": 'OK', "message": "Retirada do carinho com sucesso!"})
        else:
            return JsonResponse({"status": 'OK', "message": "Item não encontrado no Carrinho!"})
    except ItemCarrinho.DoesNotExist as e:
        print(e)
        return JsonResponse({"status": 'error', "message": "Item não encontrado no Carrinho!"})

    except Exception as e:
        print(e)
        traceback_str = traceback.format_exc()
        print(f"Erro: {traceback_str}")
        return JsonResponse({"status": 'error', "message": "Erro ao deletar do carrinho!"})
    