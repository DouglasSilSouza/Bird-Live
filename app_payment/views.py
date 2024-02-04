from .login_required_message import login_required_message_and_redirect
from ecommerce_main.products.getproducts import GetProducts
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from app_authentication.models import Cadastro
from ecommerce_cart.models import Carrinho, ItemCarrinho
from app_payment.models import Payments
from django.urls import reverse
from dls_empresa.variaveis import get_secret
from dotenv import load_dotenv
from datetime import datetime
import traceback
import json
import os

variavel = get_secret()

from .mercado_pago.mp import MercadoPago

import mercadopago
sdk = mercadopago.SDK(variavel["MP_TOKEN"])

# Load the stored environment variables
load_dotenv()

def status_rected_pay(data):
    match data:
        case 'cc_rejected_insufficient_amount':
            text = 'Saldo insuficiente'
        case 'cc_rejected_bad_filled_security_code':
            text = 'Código de segurança inválido'
        case 'cc_rejected_bad_filled_date':
            text = 'Data de vencimento inválida'
    return text

@login_required_message_and_redirect(login_url='login_view')
def process_payment(request):
    if request.method == 'POST':
        user = Cadastro.objects.filter(id=request.user.id).first()
        if request.body:
            try:
                dados = json.loads(request.body)
                mp = MercadoPago(user)
                response = mp.criar_pagamento(dados).json()
                print(response)
                match response.get('payment_type_id'):
                    case 'bank_transfer':
                        if response.get("point_of_interaction") is None:
                            data = {'code': int(response.get('status')), 'message': response.get('message')}
                        else:
                            qrcode_data  = get_qrcode(response["point_of_interaction"]["transaction_data"])
                            data = {'data': qrcode_data , 'code': 200}
                    case 'credit_card':                  
                        match response.get('status'):
                            case 'approved':
                                data = {'code': 200,'message': 'pagamento realizado com sucesso'}
                            case 'rejected':
                                status_text = status_rected_pay(response.get("status_detail", None))
                                data = {'code': 400,'message': f'Pagamento recusado pela operadora do cartão por {status_text}!'}
            
                payments = Payments.objects.create(
                    id_payment = response.get('id'),
                    user = request.user,
                    products = dados.get('description'),
                    date_created = response.get('date_created'),
                    date_approved = response.get('date_approved'),
                    date_last_updated = response.get('date_last_updated'),
                    status_payment = response.get('status'),
                    status_detail = response.get('status_detail'),
                    payment_type_id = response.get('payment_type_id'),  #Tipo de pagamento
                    payment_method_id = response.get('payment_method_id'), #Bandeira do Cartão
                    amount = dados.get('transaction_amount'),
                    installments = response.get('installments'),
                )
                payments.save()
                return JsonResponse(data)
            except json.JSONDecodeError as e:
                return JsonResponse({"error": "Erro ao decodificar JSON na solicitação.", "code": 400})
            
            except Exception as e:
                print(e)
                traceback_str = traceback.format_exc()
                print(f"Erro: {traceback_str}")
                return JsonResponse({"error": str(e), "code": 500})
            except:
                return JsonResponse({"error": response.get('message'), "code": response.get('status')})
        else:
            return JsonResponse({"error": "Corpo da solicitação vazio.", "code": 400})

@login_required_message_and_redirect(login_url='login_view')
def process_payment_pix(request):
    if request.method == "POST":
        user = Cadastro.objects.filter(id=request.user.id).first()
        try:
            if request.body:
                dados = json.loads(request.body)
                
                mp = MercadoPago(user)
                response = mp.criar_pagamento(dados).json()
                
                if response.get("point_of_interaction") is None:
                    context = {'code': int(response.get('status')), 'message': response.get('message')}

                else:
                    data = get_qrcode(response["point_of_interaction"]["transaction_data"])
                    context = {'data': data, 'code': 200}
                    payments = Payments.objects.create(
                        id_payment = response.get('id'),
                        user = request.user,
                        date_created = response.get('date_created'),
                        date_approved = response.get('date_approved'),
                        date_last_updated = response.get('date_last_updated'),
                        status_payment = response.get('status'),
                        status_detail = response.get('status_detail'),
                        payment_type_id = response.get('payment_type_id'),  #Tipo de pagamento
                        payment_method_id = response.get('payment_method_id'), #Bandeira do Cartão
                        installments = response.get('installments')
                    )
                    payments.save()

                return JsonResponse(context, safe=False)
        
            else:
                return JsonResponse({"error": "Corpo da solicitação vazio."}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Erro ao decodificar JSON na solicitação."}, status=400)
        except Exception as e:
            print(e)
            traceback_str = traceback.format_exc()
            print(f"Erro: {traceback_str}")
            return JsonResponse({"error": str(e)}, status=500)

def get_qrcode(data):
    try:
        data = {
            'qrcode_base64': data["qr_code_base64"],
            'qrcode' : data['qr_code'],
            'code': 200,
        }
    except:
        data = {
            'qrcode_base64':"Error",
            'qrcode' : "Error",
            'code': 500,
        }
    return data

@login_required_message_and_redirect(login_url='login_view')
def payment(request):
    user = Cadastro.objects.filter(id=request.user.id).first()
    cart = Carrinho.objects.get(usuario = user)
    total = cart.calcular_total()

    # Lista de campos obrigatórios
    campos_verificar = ['first_name',
                        'last_name',
                        'date_birthday',
                        'cep',
                        'endereco',
                        'number',
                        'code_area',
                        'phone',
                        'cpf_cnpj',
                        'type_document',
                        ]

    # Crie uma lista de campos vazios
    campos_vazios = []
    for campo_nome in campos_verificar:
        valor_campo = getattr(user, campo_nome)
        if valor_campo in (None, '', [], {}):
            campos_vazios.append(campo_nome)

    if not campos_vazios:
        context = {"user": user, 'total': total}
        return render(request, "app_payment/payment.html", context)
    else:
        request.session['dados_ausentes'] = campos_vazios
        return redirect(reverse('dados_ausentes'))

@login_required_message_and_redirect(login_url='login_view')
def dados_ausentes(request):
    campos_ausentes = request.session.get('dados_ausentes', None)
    user = Cadastro.objects.filter(id=request.user.id).first()
    context = {"user": user, "campos_ausentes": campos_ausentes}
    return render(request, "ecommerce_authentication/e-dados_ausentes.html", context)

@login_required_message_and_redirect(login_url='login_view')
def verificar_dados_ausentes(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        missing_fields = []

        # Lista de campos obrigatórios
        required_fields = ['nome', 'sobrenome', 'birthday', 'formEndereco', 'number', 'codearea', 'phone', 'cpf_cnpj', 'type_document', 'cep', 'bairro']

        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field.replace('birthday', 'Aniverário')
                                      .replace('number', 'Número').replace('code', 'Código de Área').replace('type_document', 'Tipo de Documento')
                                      .replace('cpf_cnpj', 'CPF/CNPJ').replace('phone', 'Telefone').title())

        if missing_fields:
            return JsonResponse({"message": f"Campos ausentes: {', '.join(missing_fields)}", "code": 400})
        try:
            user = Cadastro.objects.get(id=request.user.id)
            birthday = data.get('birthday')
            data_formatada = datetime.strptime(birthday, "%Y-%m-%d")

            user.first_name = data.get('nome')
            user.last_name = data.get('sobrenome')
            user.date_birthday = data_formatada
            user.endereco = data.get('formEndereco')
            user.number = data.get('number')
            user.complemento = data.get('complemento')
            user.code_area = data.get('codearea')
            user.phone = data.get('phone')
            user.type_document = data.get('type_document')
            user.cpf_cnpj = int(data.get('cpf_cnpj'))
            user.cep = int(data.get('cep'))
            user.bairro = data.get('bairro')

            user.save()
            del request.session['dados_ausentes']  # Limpar a sessão após obter os dados
            return JsonResponse({"message": "Clique em 'OK' para ser direcionado á página de pagamentos.","code": 200})
        except Exception as e:
            print(e)
            traceback_str = traceback.format_exc()
            print(f"Erro: {traceback_str}")
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Erro Interno", "code": 500}, status=500)

@login_required_message_and_redirect(login_url='login_view')
def endpoints_api(request):
    user = Cadastro.objects.filter(id=request.user.id).first()
    cart = Carrinho.objects.get(usuario = user)
    total = cart.calcular_total()
    infoProdutos = cart.get_itens()
    
    try:
        data = {
            "public_key": variavel["MP_PUBLIC_KEY"],
            "total": total,
            "infoProdutos": infoProdutos
        }
    except Exception as e:
            print(e)
            traceback_str = traceback.format_exc()
            print(f"Erro: {traceback_str}")
    return JsonResponse(data)

@csrf_exempt
def notifications_payments(request):
    if request.method == 'GET':
        topic = request.GET.get('topic')
        id = request.GET.get('id')

        print(request.body)

        if topic and id:
            return HttpResponse(topic, id, content_type='text/plain', status=200)
    elif request.method == 'POST':
        print(request)
        print(json.loads(request.body))
        return HttpResponse(status=200)

    else:
        return HttpResponse(status=500)

@login_required_message_and_redirect(login_url='login_view')
def pagamento_feito(request):
    user = Cadastro.objects.get(pk=request.user.id)
    try:
        cart = Carrinho.objects.get(usuario=user)
        itens_cart = ItemCarrinho.objects.filter(carrinho=cart)
        itens_cart.delete()
        cart.delete()
    except:
        pass

    pagamento = Payments.objects.filter(user=user).order_by('-date_created').first()
    context = {"pagamento": pagamento}

    return render(request, 'app_payment/pagamento_feito.html', context)

