from app_whats.models import Destinatario, Conversa, Mensagem, Files_WhatsApp_Message
from telebot.types import KeyboardButton, ReplyKeyboardMarkup,ReplyKeyboardRemove
from django.core.exceptions import ObjectDoesNotExist
from channels.layers import get_channel_layer
from .receber_dados_tl import ReceberDados_tl
from django.db.utils import IntegrityError
from asgiref.sync import async_to_sync
from django.conf import settings
from datetime import datetime
import traceback
import requests
import telebot
import json
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
tl_bot = telebot
bot = telebot.TeleBot(BOT_TOKEN)

# Remova o webhook anterior (opcional, se necessário)
# bot.remove_webhook()

# Defina o novo webhook
webhook_url = f'{settings.CSRF_TRUSTED_ORIGINS[0]}/telegram_webhook/'
bot.set_webhook(url=webhook_url)

enviar_atendimento = False
primeira_msg = True

@bot.message_handler(commands=['start', 'hello'])
def enviar_bemvindo(message):
    bot.send_message(message.chat.id, f"Olá {message.from_user.first_name} Tudo bem com voçê?")
    bot.reply_to(message, "Olá! Eu sou o seu bot.")
    global primeira_msg
    primeira_msg = False

    try:
        nome = message.from_user.first_name
        sobrenome = message.from_user.last_name
        desti = Destinatario.objects.get(nome_destinatario = f'{nome} {sobrenome}')
        if desti.numero_telefone_telegram is None and desti.telegram_id is None:
            primeiro_contato(message)
        else:
            menu(message)

    except Destinatario.DoesNotExist:
        primeiro_contato(message)

def primeiro_contato(message):
        text = "Identifiquei que é seu primeiro contato\nClique no botão abaixo para compartilhar seu contato:"
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        contact_button = KeyboardButton(text="Compartilhar Contato", request_contact=True)
        markup.add(contact_button)
        bot.send_message(message.chat.id,text, reply_markup=markup)

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_contact = message

    contact = user_contact.contact.phone_number # Telefone da conversa
    contato = contact.replace("+", "")
    nome = user_contact.from_user.first_name
    sobrenome = user_contact.from_user.last_name

    #Verificar se o destinatário já existe
    # Atualizar ou criar o destinatário
    global destinatario
    destinatario, _ = Destinatario.objects.update_or_create(
            nome_destinatario= f'{nome} {sobrenome}',
            defaults={
                'telegram_id': user_contact.chat.id,
                'numero_telefone_telegram': contato,
                'nome_destinatario': f'{nome} {sobrenome}',
            }
    )

    markup = ReplyKeyboardRemove()
    text = bot.send_message(message.chat.id, "Contato recebido\nEstou encaminhando nosso menu", reply_markup=markup, parse_mode='MarkDown')
    menu(text)

@bot.message_handler(commands=['cep'])
@bot.message_handler(func=lambda message: message.text.lower() == "cep")
def buscar_cep(message):
    if message.text.lower() == 'menu':
        bot.send_message(message.chat.id, "Retornando ao menu.")
        return message

    mensagem = "Digite um CEP para pesquisa:"
    markup = ReplyKeyboardRemove()
    env_msg = bot.send_message(message.chat.id, mensagem, parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler(env_msg, buscando_cep)
    return message

def buscando_cep(message):
    cep = message.text
    cep = cep.strip().replace("-", "").replace(" ", "")

    if cep.isalpha():
        text = 'Digite apenas números!'
    elif not cep.isnumeric():
        text = 'CEP inválido, envie novamente!\nDigite /menu para voltar ao ínicio'
    elif int(len(cep)) < 8:
        text = 'CEP inválido, envie novamente!\nDigite /menu para voltar ao ínicio'

    else:
        url = f'https://brasilapi.com.br/api/cep/v1/{cep}'
        response = requests.get(url).json()
        cep = response.get('cep')
        estado = response.get('state')
        cidade = response.get('city')
        bairro = response.get('neighborhood')
        rua = response.get('street')
        servico_postal = response.get('service')
        text = f"CEP: {cep[:5]}-{cep[5:]}\nEstado: {estado}\nCidade: {cidade}\nBairro: {bairro}\nRua: {rua}\nServiço Postal: {servico_postal}\n\nDigite /menu para voltar ao ínicio"

    bot.send_message(message.chat.id, text)
    return message

@bot.message_handler(commands=['menu'])
def menu(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buscar_cep = KeyboardButton("Cep")
    atendimento = KeyboardButton("Atendimento")
    opcao3 = KeyboardButton("Opção 3")

    markup.add(buscar_cep, atendimento, opcao3)

    bot.send_message(message.chat.id, "Escolha uma das opções abaixo:", reply_markup=markup)
    return message

@bot.message_handler(func=lambda message: message.text == "Atendimento")
def handle_atendimento(message):
    global enviar_atendimento
    if not enviar_atendimento:
        enviar_atendimento = True
        bot.reply_to(message, "Estou enviando seu atendimento ao nosso time.")


@bot.message_handler(func=lambda message: message.text == "Opção 3")
def handle_option3(message):
    msg = bot.send_message(message.chat.id, "Você escolheu a Opção 3. Executando a função correspondente.")
    menu(msg)

def fim_atendimento(message):
    handle_atendimento(message)
    if enviar_atendimento:
        enviar_atendimento = False
        bot.reply_to(message, "Olá novamente, estarei encaminhando nosso menu: ")
        menu(message=message)

@bot.message_handler(func=lambda msg: True)
def handle_message(message):

    if primeira_msg:
        enviar_bemvindo(message)

    if not enviar_atendimento:
        bot.send_message(message.chat.id, "Desculpe não entendi a mensagem, caso precise envie /menu para mostrar o menu de opções.")
    else:
        dados = ReceberDados_tl(message).receber_mensagem()
    
def handle_enviar_modelo(chat_id, message):
    response = bot.send_message(chat_id, message)
    return response

# print("Iniciando Bot...")
# bot.infinity_polling()
# print("Encerrando bot...")