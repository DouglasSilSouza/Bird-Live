from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from .login_required_message import login_required_message_and_redirect
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from .models import Cadastro
import re

from django.contrib.auth import authenticate, login, get_user_model

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not (email and password):
            messages.error(request, 'Por favor, preencha todos os campos.', extra_tags='error')
        else:
            user = authenticate(email=email, password=password)

            if user is not None:
                login(request, user)
                if user.is_colaborador:
                    return redirect('home')  # Use o nome da rota diretamente
                else:
                    return redirect('e-home')  # Use o nome da rota diretamente
            else:
                messages.error(request, 'Credenciais inválidas. Por favor, tente novamente.', extra_tags='error')
    return render(request, 'ecommerce_authentication/e-login.html')  # Substitua 'seu_template.html' pelo nome correto do seu template

def enviar_email(email):
    dados = Cadastro.objects.filter(email=email).first()
    mensagem = "E-mail Teste"
    try:
        mail = EmailMessage(subject=dados.first_name, body=mensagem,
                                from_email=settings.EMAIL_HOST_USER,
                                to=[email])
        mail.send()
        status = "success"
        text = "Caso Exista esse E-mail em nossas bases verifique sua caixa de entrada, foi enviado uma mensagem para o E-mail fornecido!"
    except Exception as e:
        print(e)
        status = "error"
        text = "Erro ao enviar E-mail"
        print(text)
    return status, text

def login_view_colab(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        User = get_user_model()
        user = User.objects.filter(email=email).first()

        if email == '' and password == '':
            messages.error(request, 'Digite para poder acessar!', extra_tags='error')
        elif user is None:
            messages.error(request, 'Usuário não existe!', extra_tags='error')
        else:
            auth_user = authenticate(request, email=email, password=password)
            if auth_user is not None:
                usuario = Cadastro.objects.get(email=email)
                login(request, auth_user)
                if usuario.is_colaborador:
                    return redirect(reverse('home'))
                else:
                    return redirect(reverse('e-home'))
            else:
                messages.error(request, 'Senha incorreta!', extra_tags='error')

    return render(request, 'app_authentication/login_view.html')

@login_required_message_and_redirect(login_url='login_view')
def logout_view(request):
    logout(request)
    messages.success(request,'Desconectado com sucesso!', extra_tags='success')
    return redirect(reverse('login_view'))

def cadastro_colaborador(request):
    regex_email = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
    regex_senha = re.compile(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$")

    if request.method == 'POST':
        nome = request.POST.get('first_name')
        sobrenome = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        conf_password = request.POST.get('conf_password')

        is_user_string = request.POST.get('is_user')
        is_user = bool(is_user_string)

        is_colaborador = True

        user_bd = Cadastro.objects.filter(email=email)

        if not (nome, email, sobrenome, password, conf_password):
            messages.error(request, "Possui algum campo em branco!", extra_tags="error")
        elif password != conf_password:
            messages.error(request, "Senhas não coincidem!", extra_tags="error")
        elif not re.fullmatch(regex_email, email):
            messages.error(request, "E-mail inválido!", extra_tags="error")
        elif not re.fullmatch(regex_senha, password):
            messages.error(request, "Senha não contém uma letra maiúscula, minúscula e caracte especial.!", extra_tags="error")
        elif len(nome) <= 3:
            messages.error(request, "Nome Inválido!", extra_tags="error")
        elif len(sobrenome) <= 3:
            messages.error(request, "Sobrenome Inválido!", extra_tags="error")
        elif user_bd.exists():
            messages.error(request, "Usuário já cadastrado!", extra_tags="error")
        elif is_user:
            return redirect(reverse('cadastro_user'))
        else:
            user = Cadastro(
                email=email,
                username=nome,
                first_name=nome,
                last_name=sobrenome,
                password=make_password(password),
                is_active = False,
                is_colaborador = is_colaborador
            )
            user.save()
            if not is_user:
                user.user_permissions.add('app_authentication.can_access_colaborador_pages')
            messages.success(request, "Usuario cadastrado com sucesso!", extra_tags="success")
            return redirect(reverse('login_view'))
    else:
        return render(request, 'app_authentication/cadastro.html')

def cadastro_usuario(request):
    regex_email = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
    regex_senha = re.compile(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$")

    if request.method == 'POST':
        nome = request.POST.get('first_name')
        sobrenome = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        conf_password = request.POST.get('conf_password')
        telefone = request.POST.get('telefone')
        documento = request.POST.get('documento')
        num_documento = request.POST.get('numero_documento')
        sexo = request.POST.get('sexo')
        endereco = request.POST.get('endereco')
        numero = request.POST.get('numero')
        cep = request.POST.get('cep').replace("-", "")
        nascimento = request.POST.get('nasc')
        is_colaborador = False

        is_user_string = request.POST.get('is_user')
        is_user = bool(is_user_string)

        user_bd = Cadastro.objects.filter(email=email)

        if not (nome, email, sobrenome, password, conf_password):
            messages.error(request, "Possui algum campo em branco!", extra_tags="error")
            #return JsonResponse({"message": "Possui algum campo em branco!", "status": 400})
        elif password != conf_password:
            messages.error(request, "Senhas não coincidem!", extra_tags="error")
            #return JsonResponse({"message": "Senhas não coincidem!", "status": 400})
        elif not re.fullmatch(regex_email, email):
            messages.error(request, "E-mail inválido!", extra_tags="error")
            #return JsonResponse({"message": "E-mail inválido!", "status": 400})
        elif not re.fullmatch(regex_senha, password):
            messages.error(request, "Senha não contém uma letra maiúscula, minúscula e caracte especial.!", extra_tags="error")
            #return JsonResponse({"message": "Senha não contém uma letra maiúscula, minúscula e caracte especial.!", "status": 400})
        elif len(nome) <= 3:
            messages.error(request, "Nome Inválido!", extra_tags="error")
            #return JsonResponse({"message": "Nome Inválido!", "status": 400})
        elif len(sobrenome) <= 3:
            messages.error(request, "Sobrenome Inválido!", extra_tags="error")
            #return JsonResponse({"message": "Sobrenome Inválido!", "status": 400})
        elif user_bd.exists():
            messages.error(request, "Usuário já cadastrado!", extra_tags="error")
            #return JsonResponse({"message": "Usuário já cadastrado!", "status": 400}) 
        elif not (telefone, documento, num_documento, sexo, endereco, numero, cep, nascimento):
            messages.error(request, "Possui algum campo em branco!", extra_tags="error")
            #return JsonResponse({"message": "Possui algum campo em branco!", "status": 400})
        else:
            # Encontrando o DDD usando expressões regulares
            ddd = re.search(r'\((\d{2})\)', telefone).group(1)

            # Removendo os parênteses e traço
            telefone_limpo = re.sub(r'[()-]', '', telefone)
            
            user = Cadastro(
                email=email,
                username=nome,
                first_name=nome,
                last_name=sobrenome,
                password=make_password(password),
                is_active = True,
                code_area = ddd,
                phone = telefone_limpo,
                type_document = documento,
                cpf_cnpj = num_documento,
                date_birthday = nascimento,
                cep = cep,
                endereco = endereco,
                number = numero,
                is_colaborador = is_colaborador
            )
            user.save()
            messages.success(request, "Usuario cadastrado com sucesso!", extra_tags="success")
            return redirect(reverse('login_view'))
    return render(request, 'ecommerce_authentication/e-cadastro.html')

@login_required_message_and_redirect(login_url='login_view')
def configuracoes(request):

    form_senha = SetPasswordForm(request.user, request.POST)

    if request.method == "POST":
        nome = request.POST.get('password')
        sobrenome = request.POST.get('passconfirmation')
        email = request.POST.get('email')

        if nome.isalpha() or sobrenome.isalpha:
            messages.error(request, "Coloque somente letras!")
        elif nome == "" and sobrenome == "":
            messages.error(request, "Campo não pode estar em branco!")
        elif re.search(r'[a-zA-Z0-9_-]+@[a-zA-Z0-9]+\.[a-zA-Z]{1,3}$', email):
            messages.error(request, "Digite um E-mail válido!")
        elif email == "":
            messages.error(request, "E-mail não pode estar em branco!")

        else:
            try:
                user = get_object_or_404(Cadastro, pk=request.user.id)
                user.email = email
                user.last_name = sobrenome
                user.first_name = nome
                user.save()
                messages.success(request,'Dado(s) atualizado com sucesso!')
            except Exception as e:
                messages.error(request,'Houve algum erro ao tentar alterar os dados!')
        
        if form_senha.is_valid():
                user = form_senha.save()
                update_session_auth_hash(request, user)
                return redirect('alterar_senha')
        else:
            form_senha = SetPasswordForm(request.user)
    
    return render(request, 'app_whats/configuracoes.html', {'form_senha': form_senha})
