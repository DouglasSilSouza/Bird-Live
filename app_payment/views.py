from ssl import create_default_context
from .login_required_message import login_required_message_and_redirect
from ecommerce_cart.models import Carrinho, ItemCarrinho
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from app_payment.models import Payments
from .gerencianet.efi import Pagamento
from django.shortcuts import render
from django.utils import timezone
from decimal import Decimal
import traceback
import dotenv
import json
import os

dotenv.load_dotenv()

@csrf_exempt
def imprimir(request):
    if request.method == "POST":
        return HttpResponse(status=200)

@login_required_message_and_redirect(login_url="login_view")
@csrf_exempt
def enviar_conf_conta(request):
    try:
        count = os.getenv("IDENT_CONTA")
        transform = {"count": count}
        return JsonResponse(transform)
    except Exception as e:
        print(e)
        return JsonResponse({"Error": e})

@csrf_exempt
def imprimirPix(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            txid = data['pix'][0]['txid']
            pagamentos = Pagamento().pix_detail(txid)
            pay = Payments.objects.get(txid_pix=txid)
            pay.status_detail = pagamentos['status']
            pay.save()

            with open("data.txt", "a") as outfile:
                outfile.write("\n")
                json.dump(data, outfile)
            return HttpResponse(status=200)
        except Exception as e:
            error_message = str(e)
            traceback.print_exc()
            print(f"Erro no código principal: {e}")
            print(error_message)
            return JsonResponse({"erro": error_message}, safe=False, status=404)

@csrf_exempt
def notificacaoCobrancas(request):
    notification = request.POST.get('notification')
    pagamentos = Pagamento()
    get_notification = pagamentos.get_notification_cobranca(notification)
    return HttpResponse(status=200)

@login_required_message_and_redirect(login_url="login_view")
def flagscard(request):
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

@login_required_message_and_redirect(login_url="login_view")
def page_payments(request):
    user = request.user
    carrinho = Carrinho.objects.get(usuario=user)
    items = ItemCarrinho.objects.filter(carrinho=carrinho)
    context = {
        "dados": user,
        "items": items,
        "cart": carrinho,
    }
    return render(request, "app_payment/payment.html", context)

@login_required_message_and_redirect(login_url="login_view")
def criar_pagamento_pix(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            cartid = body.get('cartid')
            pagamento = Pagamento(int(cartid))
            try:
                creat = pagamento.creat_pay_pix()
                responses = creat.get("loc").get("id")
                qrcode = pagamento.creat_qrcode_pix(responses)
                dados = json.dumps(qrcode)

                itens = Carrinho.objects.get(usuario=request.user).get_itens()
                pay = Payments.objects.create(
                    txid_pix = creat['txid'],
                    user = request.user,
                    products = itens,
                    date_created = creat['calendario']['criacao'],
                    id_payment = creat['loc']['id'],
                    interest_free_value = creat['valor']['original'],
                    status_payment = "pix",
                    status_detail = creat['status']
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
def criar_pagamento_cartao(request):
    body = json.loads(request.body)
    if request.method == "POST":
        cartID = body.get('carrinhoid')
        try:
            itens = Carrinho.objects.get(usuario=request.user).get_itens()
            pagamento = Pagamento(int(cartID))
            cartao = pagamento.creat_pay_cartao()
            if cartao.get('code') == 200:
                date_now = timezone.now()
                date = date_now.strftime('%Y-%m-%dT%H:%M:%SZ')
                pay, created = Payments.objects.get_or_create(
                    id_payment = cartao['data']['charge_id'],
                    defaults= {
                        "user": request.user,
                        "status_detail" : cartao['data']['status'],
                        "interest_free_value" : Decimal(cartao['data']['total']) / 100 ,
                        "date_created" : cartao['data']['created_at'],
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
def conclusao_pagamento_cartao(request):
    body = json.loads(request.body)
    if request.method == "POST":
        cartID = body.get('carrinhoid')
        parcela = body.get('parcela')
        token = body.get('token')
        charge_id = body.get('charge_id')
        try:
            pagamento = Pagamento(cartID)
            cartao = pagamento.complete_payment_card(parcela, token, charge_id)
            if cartao.get('code') == 200:
                try:
                    pay, created = Payments.objects.get_or_create(id_payment=charge_id, defaults= {
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

                    print(f"{cartao} Erro cartão")
                    return JsonResponse(cartao, safe=False, status=200)
                except Payments.DoesNotExist:
                    traceback.print_exc()
                    print("Objeto não encontrado")
                    return JsonResponse({"erro":"Objeto não encontrado"}, safe=False, status=404)
                except Exception as e:
                    error_message = str(e)
                    traceback.print_exc()
                    print("Erro de execução")
                    print(error_message)
                    return JsonResponse({"erro": error_message}, safe=False, status=404)
            else:
                print(f"Outro código erro: {cartao}", type(cartao))
                return JsonResponse(cartao, safe=False, status=404)
        except Exception as e:
            error_message = str(e)
            traceback.print_exc()
            print(f"Erro no código principal: {e}")
            print(error_message)
            return JsonResponse({"erro": error_message}, safe=False, status=404)

@login_required_message_and_redirect(login_url="login_view")
def pagamento_concluido(request, charge_id):
    pay = Payments.objects.get(id_payment=charge_id)
    return render(request, "app_payment/pagamento_feito.html", {"pay": pay})

@login_required_message_and_redirect(login_url="login_view")
def listando(request):
    pagamento = Pagamento(18)
    action = pagamento.list_webhook()
    print(action)
    return HttpResponse(pagamento)
