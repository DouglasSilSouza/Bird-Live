from multiprocessing import context
from .login_required_message import login_required_message_and_redirect
from ecommerce_main.products.getproducts import GetProducts
from app_authentication.models import Cadastro
from ecommerce_cart.models import Carrinho, ItemCarrinho
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
import traceback
import json

# Create your views here.
@login_required_message_and_redirect(login_url='login_view')
def carrinho(request):
    cart = ""
    items = ""
    if request.method == "GET":
        try:
            user =request.user
            cart = Carrinho.objects.get(usuario=user)
            items = ItemCarrinho.objects.filter(carrinho=cart)
        except Carrinho.DoesNotExist:
            print("Carrinho não encontrado")
        except Carrinho.MultipleObjectsReturned:
            print("Múltiplos carrinhos encontrados")
    return render(request, "ecommerce_cart/e-cart.html",  {"items": items, "cart": cart})

@login_required_message_and_redirect(login_url='login_view')
@csrf_exempt
def atualizar_quantidade(request):
    try:
        body = json.loads(request.body)
        produto_id = int(body.get('idProduto'))
        qtd = int(body.get('qtd'))

        # Validando se os campos necessários estão presentes
        if produto_id is None or qtd is None:
            return JsonResponse({"msg": "Campos idProduto e qtd são obrigatórios", "status": 400})

        # Utilizando get_object_or_404 para simplificar a obtenção do item
        item = get_object_or_404(ItemCarrinho, produto_id=produto_id)
        item.quantidade = qtd
        item.save()

        return JsonResponse({"msg": "Atualizado com sucesso", "status": 200})
    
    except json.JSONDecodeError as e:
        return JsonResponse({"msg": f"Erro ao decodificar JSON: {e}", "status": 400})
    
    except ValueError as e:
        return JsonResponse({"msg": f"Erro ao converter valores: {e}", "status": 400})
    
    except ItemCarrinho.DoesNotExist as e:
        return JsonResponse({"msg": f"Item do carrinho não encontrado: {e}", "status": 404})
    
    except Exception as e:
        return JsonResponse({"msg": f"Erro desconhecido: {e}", "status": 500})

@login_required_message_and_redirect(login_url='login_view')
def getdatacart(request):
    body = json.loads(request.body)
    try:
        user = Cadastro.objects.get(pk = request.user.id)
        cart, _ = Carrinho.objects.get_or_create(usuario = user)
        id_product = int(body.get('idProduct'))
        products = GetProducts(id_product).get_products()

        #subtotal = products.get('price') * int(body.get('qtd'))

        item_cart, created = ItemCarrinho.objects.get_or_create(produto_id = id_product, 
            defaults={
                "carrinho": cart,
                "quantidade": int(body.get('qtd')),
                "title": products.get('title'),
                "description": products.get('description'),
                "image_url": products.get('image'),
                "valor_unitario": float(products.get('price')),
                #"subtotal": float(subtotal),
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
    