from .models import Mensagem, Conversa, Destinatario, Files_WhatsApp_Message
from .login_required_message import login_required_message_and_redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from .whatsapp.receber_dados import Receber_dados
from .telegram.telegram_bot import bot, tl_bot, handle_enviar_modelo
from .telegram.models_telegram import modelos_telegram
from django.shortcuts import render, redirect
from django.db.utils import IntegrityError
from .whatsapp.conn import Conn_Whatsapp
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from datetime import datetime
import traceback
import base64
import json
import os
import re

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def home(request):
    return render(request, 'app_products/product_index.html')

@login_required_message_and_redirect(login_url='login_view')
def chat_window(request):
    return render(request, 'app_whats/chat.html')

@login_required_message_and_redirect(login_url='login_view')
def iniciar_chat(request):

    numero = ""
    model = ""

    if request.method == 'POST':
        numero = request.POST.get("numero").replace("(", "").replace(")", "").replace("-", "")
        numero = "".join(numero.split())
        if len(numero) == 11:
                numero = '55' + numero
        model = request.POST.get("model")
        canal = request.POST.get("canal")

        print(canal)

        if not numero:
            messages.error(request, 'Campo em Branco, por favor digite um número!')
            return redirect(reverse('iniciar_chat'))
        elif len(numero) < 13:
            messages.error(request, 'Digite um número válido!')
            return redirect(reverse('iniciar_chat'))
        elif not model:
            messages.error(request, 'Modelo em Branco, por favor selecione um modelo!')
            return redirect(reverse('iniciar_chat'))
        elif not numero.isdigit():
            messages.error(request, 'Digite apenas números!')
            return redirect(reverse('iniciar_chat'))
        else:
            if canal == '' and not canal:
                messages.error(request, 'Selecione um canal de mensagens!')
                return redirect(reverse('iniciar_chat'))
            else:
                if canal == 'telegram':
                    nome = None
                    try:
                        dest = Destinatario.objects.filter(numero_telefone_telegram=numero)
                        if model == 'inicio':
                            nome = dest.first().nome_destinatario

                        try:
                            modelo = modelos_telegram(model)

                            id_telegram = dest.first().telegram_id
                            response = handle_enviar_modelo(id_telegram, modelo)
                            if response:
                                destinatario, _ = Destinatario.objects.get_or_create(numero_telefone_telegram=numero)
                                conversa, _ = Conversa.objects.get_or_create(identificador_conversa=f"conversa_{numero}", usuario=request.user, destinatario=destinatario, status_room='novo', canal='whatsapp')

                                # Salvar a mensagem no banco de dados
                                Mensagem.objects.create(
                                    conversa=conversa,
                                    conteudo='Enviado Modelo',
                                    data_hora_message=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                    tipo='modelo',
                                    wa_id_message= response.message_id,
                                )

                                request.session['numero_usuario'] = numero
                                return redirect(reverse('send_whatsapp_message'))
                            else:
                                messages.error(request, f"<strong>Erro ao enviar a mensagem </strong>: {msg_error.get('error').get('message')}<br><strong>Code </strong>: {msg_error.get('error').get('code')}<br><strong>status</strong> : {response.status_code}")
                                return redirect(reverse('iniciar_chat'))

                        except Exception as e:
                            print(e)
                            # Erro interno
                            traceback_str = traceback.format_exc()
                            print(f"Erro: {traceback_str}")
                            messages.error(request, f"Erro interno: {e} | status: 500")
                            return redirect(reverse('iniciar_chat'))

                    except Destinatario.DoesNotExist:
                        messages.error(request, f"Usuario/Contato não encontrato pelo Telegram!")

                elif canal == 'whatsapp':
                    nome = None
                    dest = Destinatario.objects.filter(numero_telefone_whatsapp=numero)
                    if model == 'inicio':
                        nome = dest.first().nome_destinatario
                    try:
                        conn = Conn_Whatsapp()
                        response = conn.enviar_modelo(numero, model, nome)
                        if response.status_code == 200:

                            response_json = response.json()

                            destinatario, _ = Destinatario.objects.get_or_create(numero_telefone_whatsapp=numero)
                            conversa, _ = Conversa.objects.get_or_create(identificador_conversa=f"conversa_{numero}", usuario=request.user, destinatario=destinatario, status_room='novo', canal='whatsapp')

                            # Salvar a mensagem no banco de dados
                            Mensagem.objects.create(
                                conversa=conversa,
                                conteudo='Enviado Modelo',
                                data_hora_message=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                tipo='modelo',
                                wa_id_message= response_json.get('messages')[0].get('id'),
                            )

                            request.session['numero_usuario'] = numero
                            return redirect(reverse('send_whatsapp_message'))
                        else:
                            # Erro ao enviar a mensagem
                            msg_error = response.json()
                            if msg_error.get('error').get('code') == 131030:
                                messages.error(request, f"<strong>Erro ao enviar a mensagem </strong>: {msg_error.get('error').get('error_data').get('details')} <br> <strong>Detalhes</strong>: {msg_error.get('error').get('message')}<br><strong>Code</strong>: {msg_error.get('error').get('code')}<br><strong>status</strong>: {response.status_code}")
                            else:
                                messages.error(request, f"<strong>Erro ao enviar a mensagem </strong>: {msg_error.get('error').get('message')}<br><strong>Code </strong>: {msg_error.get('error').get('code')}<br><strong>status</strong> : {response.status_code}")
                            return redirect(reverse('iniciar_chat'))
                    except Exception as e:
                        print(e)
                        # Erro interno
                        traceback_str = traceback.format_exc()
                        print(f"Erro: {traceback_str}")
                        messages.error(request, f"Erro interno: {e} | status: 500")
                        return redirect(reverse('iniciar_chat'))
                else:
                    messages.error(request, "Selecione um canal!")
                    return redirect(reverse('iniciar_chat'))
    else:
        return render(request, 'app_whats/get_numero.html')

@csrf_exempt
def verify_webhook(request, user=None):
    if request.method == 'GET':
        verify_token = "TESTE_API"  # Atualize com o seu verify token

        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == verify_token:
            return HttpResponse(challenge, content_type='text/plain', status=200)
        else:
            return HttpResponse(status=403)
    elif request.method == 'POST':
        body = request.body.decode('utf-8')
        payload = json.loads(body)
        data = payload.get('entry')[0].get('changes')[0].get('value')
        if data is not None:
            messages = data.get('messages')
            if messages is not None and len(messages) > 0:
                message_type = messages[0].get('type')
                if message_type == 'text':
                    dados = Receber_dados(data).receber_mensagem()

                elif message_type == 'image':
                    file = Receber_dados(data).receveid_file()

            elif data.get('statuses'):
                statuses = Receber_dados(data).status_messages()
        else:
            print("Erro: Objeto é NONE")

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)

@login_required_message_and_redirect(login_url='login_view')
@csrf_exempt
def send_whatsapp_message(request):
    if request.method == "POST":
        print(request)
        return render(request, 'app_whats/chat_whatsapp.html')
    #     json_data = json.loads(request.body)
    #     numero = json_data.get('numero')
    #     mensagem = json_data.get('mensagem')
    #     datahora = json_data.get('datahora')
    #     data_hora = datetime.strptime(datahora, "%d/%m/%Y %H:%M").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    #     type_conteudo = json_data.get('type_conteudo')

    #     print(json_data)

    #     if mensagem is None or mensagem == '':
    #         messages.error(request, 'Mensagem em Branco!', extra_tags='error')
    #         return render(request, 'app_whats/chat_whatsapp.html')
    #     elif type_conteudo is None or type_conteudo == '':
    #         messages.error(request, 'Tipo em Branco!', extra_tags='error')
    #         return render(request, 'app_whats/chat_whatsapp.html')
    #     else:
    #         try:
    #             conn = Conn_Whatsapp()
    #             if type_conteudo == 'text':
    #                 response = conn.enviar_mensagem(numero, mensagem)
    #                 files_msg = None
    #             elif type_conteudo == 'image':
    #                 data_message = json.loads(mensagem)
    #                 code_imagem = data_message.get('codeimage')
    #                 response = conn.send_image(numero, code_imagem)
    #                 response, id_image = response
    #                 if response.status_code == 200:
    #                     try:
    #                         # Extrair o formato da imagem da string base64
    #                         format_match = re.search(r"data:image/(\w+);base64,", code_imagem)
    #                         image_format = format_match.group(1)

    #                         # Remover o prefixo da string base64
    #                         base64_data = re.sub(r"data:image/(\w+);base64,", "", code_imagem)

    #                         # Decodificar a string base64 para bytes
    #                         image_data = base64.b64decode(base64_data)

    #                         # Calcular o tamanho da imagem em bytes
    #                         image_size = len(image_data)
    #                         mensagem = None
    #                         # Salva o arquivo temporário no campo file_message
    #                         files_msg = Files_WhatsApp_Message.objects.create(
    #                             file_type=f"image/{image_format}",
    #                             file_size=image_size,
    #                             file_id_whatsapp=id_image.get('id'),
    #                             file_message= base64_data,
    #                         )
    #                         print("Sucesso ao salvar a imagem!")

    #                     except IntegrityError as e:
    #                         print(f'ERRO ao Salvar: {e}')
    #                         return None
    #                 else: print(f'ERRO ao Salvar a Imagem no Banco de dados!')
                    
    #             response_json = response.json()
    #             if response.status_code == 200:

    #                 destinatario, _ = Destinatario.objects.get_or_create(numero_telefone_whatsapp=numero)
    #                 conversa, _ = Conversa.objects.get_or_create(identificador_conversa=f"conversa_{numero}", usuario=request.user, destinatario=destinatario, status_room='novo')

    #                 wa_id_message = response_json.get('messages')[0].get('id')                      

    #                 # Salvar a mensagem no banco de dados
    #                 Mensagem.objects.create(
    #                     conversa=conversa,
    #                     conteudo=mensagem,
    #                     data_hora_message=data_hora,
    #                     tipo='enviada',
    #                     wa_id_message=wa_id_message,
    #                     files = files_msg,
    #                 )
    #                 return JsonResponse({"wa_id_message": wa_id_message, "status_response": 200})
    #             else:
    #                 # Erro ao enviar a mensagem
    #                 print(f"Erro ao enviar a mensagem (Lado Cliente): {response.text} | status: {response.status_code}")
    #                 return JsonResponse({"mensagem": f"Erro ao enviar a mensagem (Lado Cliente): {response_json.get('error').get('message')} | code: {response_json.get('error').get('code')}", "status_response": response.status_code})
    #         except Exception as e:
    #             print(e)
    #             traceback_str = traceback.format_exc()
    #             print(f"Erro: {traceback_str}")
    #             # Erro interno
    #             return JsonResponse({"mensagem": f"Erro interno: {e} | status: 500", "status_response": 500})
    else:
    #     numero = request.session.get('numero_usuario')
    #     destinatario_ = Destinatario.objects.get(numero_telefone_whatsapp = numero)
    #     conversas = Conversa.objects.filter(identificador_conversa=f"conversa_{numero}", status_room='Novo')
    #     msg = Mensagem.objects.filter(conversa__in=conversas).order_by('id')
    #     context = {
    #         'msg': msg,
    #         'destinatario': destinatario_,
    #         'data_conversa': [conv.data_conversa.strftime("%d/%m/%Y") for conv in conversas][0],
    #     }
        return render(request, 'app_whats/chat_whatsapp.html')

@login_required_message_and_redirect(login_url='login_view')
@csrf_exempt
def send_telegram_message(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)


@login_required_message_and_redirect(login_url='login_view')
def encerrar_atendimento(request, numero):
    if request.method == 'POST':
        finalizar = request.POST.get('finalizar')
        mensagem = "Atendimento finalizado!"

        if finalizar == 'True':
            try:
                conn = Conn_Whatsapp()
                response = conn.enviar_mensagem(numero, mensagem)

                if response.status_code == 200:
                    conv = Conversa.objects.get(identificador_conversa=f"conversa_{numero}", status_room='Novo')
                    conv.status_room=f"Encerrado ás {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                    conv.save()
                    # Salvar a mensagem no banco de dados
                    Mensagem.objects.create(
                        conversa=conv,
                        data_hora_message=datetime.now(),
                        conteudo=mensagem,
                        tipo= "finalizado"
                    )
                    messages.success(request, "Atendimento encerrado com sucesso!")
                else:
                    messages.error(request, f"Erro ao enviar a mensagem (Lado Cliente): {response.text} | status: {response.status_code}")
            except Exception as e:
                print(e)
                traceback_str = traceback.format_exc()
                print(f"Erro: {traceback_str}")
                # Erro interno
                messages.error(request, f"Erro interno: {e} | status: 500")
        else:
            
            messages.error(request, "Erro pois o botão é False!")
    return redirect(reverse('iniciar_chat'))

@login_required_message_and_redirect(login_url='login_view')
def conversas_whatsapp(request):
    conversas = Conversa.objects.filter(usuario=request.user)
    context = {
        'conversas': conversas
    }
    return render(request, 'app_whats/conversas.html', context)

@login_required_message_and_redirect(login_url='login_view')
def ver_histórico(request, id):
    conversa = Conversa.objects.get(id=id)
    msg = Mensagem.objects.filter(conversa=conversa).order_by('data_hora_message')
    context = {
        'mensagens': msg,
        'conversa': conversa
    }
    return render(request, 'app_whats/historico.html', context)

@require_POST
@csrf_exempt
def telegram_webhook(request):
    payload =request.body.decode("UTF-8")
    update = tl_bot.types.Update.de_json(payload)
    bot.process_new_updates([update])
    return JsonResponse({"status": "ok"})
