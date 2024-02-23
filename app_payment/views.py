import re
from .login_required_message import login_required_message_and_redirect
from ecommerce_cart.models import Carrinho, ItemCarrinho
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from app_payment.models import Payments
from .gerencianet.efi import Pagamento
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render
from django.utils import timezone
from decimal import Decimal
import traceback
import dotenv
import json
import os

dotenv.load_dotenv()

@csrf_exempt
async def imprimir(request):
    if request.method == "POST":
        return HttpResponse(status=200)

@login_required_message_and_redirect(login_url="login_view")
@csrf_exempt
async def enviar_conf_conta(request):
    try:
        count = os.getenv("IDENT_CONTA")
        transform = {"count": count}
        return JsonResponse(transform)
    except Exception as e:
        print(e)
        return JsonResponse({"Error": e})

@csrf_exempt
async def enviar_notificacao_websocket(user_id, status, txid_status):
    channel_layer = get_channel_layer()
    await channel_layer.group_send( # type: ignore
        f"user_{user_id}",
        {
            'type': 'send_notification',
            'status': status,
            'txid_status': txid_status,
        }
    )

@csrf_exempt
async def imprimirPix(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            txid = data['pix'][0]['txid']
            pagamentos = Pagamento().pix_detail(txid)
            status_detail = pagamentos['status'] # type: ignore
            interest_value = pagamentos['valor']['original'] # type: ignore
            if status_detail == "CONCLUIDA":
                pay = await database_sync_to_async(Payments.objects.get)(txid_payment_token=txid)
                pay.status_detail = status_detail
                pay.interest_value = interest_value
                await database_sync_to_async(pay.save)()
                user_id = await database_sync_to_async(lambda: pay.user.id)()
                await enviar_notificacao_websocket(user_id ,status_detail, txid)


            return HttpResponse(status=200)
        except Payments.DoesNotExist as e:
            error_message = str(e)
            print(error_message)
            traceback.print_exc()
            return JsonResponse({"erro": error_message}, safe=False, status=404)
        except Exception as e:
            error_message = str(e)
            traceback.print_exc()
            return JsonResponse({"erro": error_message}, safe=False, status=404)

@csrf_exempt
async def notificacaoCobrancas(request):
    notification = request.POST.get('notification')
    pagamentos = Pagamento()
    pagamentos.get_notification_cobranca(notification)
    return HttpResponse(status=200)

@login_required_message_and_redirect(login_url="login_view")
async def flagscard(request):
    body = json.loads(request.body)
    if request.method == "POST":
        try:
            with open("app_payment/bandeiras_cartao.json", "r") as arquivo:
                dados = json.load(arquivo)

            try:
                brand = body.get("bandeira").capitalize()
                flag = dados.get(brand)
                return JsonResponse({"flag": flag})
            except Exception as e:
                return JsonResponse({'msg': "Erro ao encontrar a bandeira do cartão"})
        except Exception as e:
            print(e)
            return JsonResponse({"error": f"Erro ao enviar os dados: {e}"})

@database_sync_to_async
def get_carrinho(usuario):
    return Carrinho.objects.get(usuario=usuario)

@database_sync_to_async
def get_items(carrinho):
    return ItemCarrinho.objects.filter(carrinho=carrinho)

@login_required_message_and_redirect(login_url="login_view")
async def page_payments(request):
    user = request.user
    carrinho = await get_carrinho(user)
    items = await get_items(carrinho)
    context = {
        "dados": user,
        "items": items,
        "cart": carrinho,
    }
    return await database_sync_to_async(render)(request, "app_payment/payment.html", context)

@login_required_message_and_redirect(login_url="login_view")
async def criar_pagamento_pix(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            cartid = body.get('cartid')
            pagamento = Pagamento(int(cartid))
            await pagamento.initialize()
            try:
                creat = pagamento.creat_pay_pix()
                creat_result = await creat
                responses = creat_result.get("loc").get("id")
                qrcode = pagamento.creat_qrcode_pix(responses)
                dados = json.dumps(qrcode)

                carrinho = await get_carrinho(request.user)
                itens = await carrinho.get_itens()
                pay = await database_sync_to_async(Payments.objects.create)(
                    txid_payment_token = creat_result['txid'],
                    user = request.user,
                    products = itens,
                    date_created = creat_result['calendario']['criacao'],
                    id_payment = creat_result['loc']['id'],
                    interest_free_value = creat_result['valor']['original'],
                    status_payment = "pix",
                    status_detail = creat_result['status']
                )
                return JsonResponse(dados, safe=False)
            except Exception as e:
                error_message = str(e)
                traceback.print_exc()
                print(error_message)
                return JsonResponse({"erro": error_message}, safe=False, status=404)
        except Exception as e:
            error_message = str(e)
            traceback.print_exc()
            print(error_message)
            return JsonResponse({"erro": error_message}, safe=False, status=404)

@login_required_message_and_redirect(login_url="login_view")
async def criar_pagamento_cartao(request):
    body = json.loads(request.body)
    if request.method == "POST":
        cartID = body.get('carrinhoid')
        try:
            carrinho = await get_carrinho(request.user)
            itens = await carrinho.get_itens()
            pagamento = Pagamento(int(cartID))
            await pagamento.initialize()
            cartao = await pagamento.creat_pay_cartao()  # Modificado para ser assíncrono
            if cartao.get('code') == 200:
                date_now = timezone.now()
                date = date_now.strftime('%Y-%m-%dT%H:%M:%SZ')
                pay, created = await database_sync_to_async(Payments.objects.get_or_create)(
                    id_payment=cartao['data']['charge_id'],
                    defaults={
                        "user": request.user,
                        "status_detail": cartao['data']['status'],
                        "interest_free_value": Decimal(cartao['data']['total']) / 100,
                        "date_created": cartao['data']['created_at'],
                        "user": request.user,
                        "products": itens,
                        "date_created": date,
                    }
                )
                return JsonResponse({"charge_id": pay.id_payment}, safe=False, status=200)
            else:
                try:
                    traceback.print_exc()
                    return JsonResponse({"erro": cartao.get('error_description').get('message')}, safe=False, status=404)
                except:
                    traceback.print_exc()
                    return JsonResponse({"erro": cartao.get('error_description')}, safe=False, status=404)
        except Exception as e:
            error_message = str(e)
            traceback.print_exc()
            print(error_message)
            return JsonResponse({"erro": error_message}, safe=False, status=404)

@login_required_message_and_redirect(login_url="login_view")
async def conclusao_pagamento_cartao(request):
    body = json.loads(request.body)
    if request.method == "POST":
        cartID = body.get('carrinhoid')
        parcela = body.get('parcela')
        token = body.get('token')
        charge_id = body.get('charge_id')
        erropayment = body.get('erropayment')
        try:
            pagamento = Pagamento(cartID)
            await pagamento.initialize()
            cartao = await pagamento.complete_payment_card(parcela, token, charge_id, erropayment)  # Modificado para ser assíncrono
            if cartao.get('code') == 200:
                try:
                    pay, _ = await database_sync_to_async(Payments.objects.update_or_create)(  # Modificado para ser assíncrono
                        id_payment=charge_id,
                        defaults={
                            "installments": cartao['data']['installments'],
                            "installments_value": Decimal(cartao['data']['installment_value']) / 100,
                            "status_detail": cartao['data']['status'],
                            "interest_value": Decimal(cartao['data']['total']) / 100,
                            "status_payment": cartao['data']['payment'],
                        }
                    )
                    if cartao['data']['status'] == "approved":
                        date_now = timezone.now()
                        date = date_now.strftime('%Y-%m-%dT%H:%M:%SZ')
                        pay.date_approved = date

                    # print(f"Erro cartão: {cartao}")
                    return JsonResponse(cartao, safe=False, status=200)
                except Payments.DoesNotExist:
                    traceback.print_exc()
                    print("Objeto não encontrado")
                    return JsonResponse({"erro": "Objeto não encontrado"}, safe=False, status=404)
                except Exception as e:
                    error_message = str(e)
                    traceback.print_exc()
                    print("Erro de execução")
                    print(error_message)
                    return JsonResponse({"erro": error_message}, safe=False, status=404)
            else:
                print(f"Erro cartão: {cartao}")
                return JsonResponse(cartao, safe=False, status=404)
        except Exception as e:
            error_message = str(e)
            traceback.print_exc()
            print(f"Erro no código principal: {e}")
            print(error_message)
            return JsonResponse({"erro": error_message}, safe=False, status=404)

@login_required_message_and_redirect(login_url="login_view")
async def pagamento_concluido(request, txid_payment_token):
    pay = await database_sync_to_async(Payments.objects.get)(txid_payment_token=txid_payment_token)
    return render(request, "app_payment/pagamento_feito.html", {"pay": pay})

@login_required_message_and_redirect(login_url="login_view")
async def listando(request):
    pagamento = Pagamento(18)
    action = await pagamento.list_webhook() # type: ignore
    print(action)
    return HttpResponse(str(action))  # Convertendo action para string

