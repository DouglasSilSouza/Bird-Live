from app_authentication.login_required_message import login_required_message_and_redirect
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from ecommerce_cart.models import Carrinho, ItemCarrinho
from app_authentication.models import Cadastro
from app_payment.models import Payments
from .products.getproducts import GetProducts
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Sum
from django.contrib import messages
import asyncio
import re

# Create your views here.
async def base(request):
    if not request.user.is_authenticated:
        try:
            user = await asyncio.get_event_loop().run_in_executor(None, lambda: Cadastro.objects.get(pk=request.user.id))
            cart = await asyncio.get_event_loop().run_in_executor(None, lambda: Carrinho.objects.get(usuario=user))
            itens = await asyncio.get_event_loop().run_in_executor(None, lambda: ItemCarrinho.objects.filter(carrinho=cart).aggregate(soma=Sum('quantidade')))
            quantidade = itens['soma']
            return JsonResponse({"quantity": quantidade})
        except Carrinho.DoesNotExist:
            return JsonResponse({"quantity": 0})
        except Cadastro.DoesNotExist:
            return HttpResponse(None)

def home(request):
    data = GetProducts().get_products()
    return render(request, "ecommerce_main/e-main.html", {"data": data})

def productOnly(request, id):
    data = GetProducts(id).get_products()
    return render(request, "ecommerce_main/e-product_only.html", {"data": data})

@login_required_message_and_redirect(login_url='login_view')
def dados_pessoais(request):
    regex_email = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
    regex_senha = re.compile(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$")

    if request.method == 'POST':
        nome = request.POST.get('nome')
        sobrenome = request.POST.get('sobrenome')
        email = request.POST.get('email')
        telefone = request.POST.get('phone')
        documento = request.POST.get('type_document')
        num_documento = request.POST.get('cpf_cnpj')
        sexo = request.POST.get('sexo')
        endereco = request.POST.get('endereco')
        numero = request.POST.get('number')
        cep = request.POST.get('cep').replace("-", "")
        nascimento = request.POST.get('date_birthday')
        complemento = request.POST.get('complemento')
        bairro = request.POST.get('bairro')

        if not (nome, email, sobrenome, documento, num_documento, telefone, endereco, nascimento):
            messages.error(request, "Possui algum campo em branco!", extra_tags="error")

        elif not re.fullmatch(regex_email, email):
            messages.error(request, "E-mail inválido!", extra_tags="error")

        elif len(nome) <= 3:
            messages.error(request, "Nome Inválido!", extra_tags="error")
            
        elif len(sobrenome) <= 3:
            messages.error(request, "Sobrenome Inválido!", extra_tags="error")

        elif not (telefone, documento, num_documento, sexo, endereco, numero, cep, nascimento):
            messages.error(request, "Possui algum campo em branco!", extra_tags="error")

        else:
            # Encontrando o DDD usando expressões regulares
            ddd = re.search(r'\((\d{2})\)', telefone).group(1)

            # Removendo os parênteses e traço
            telefone_limpo = re.sub(r'[()-]', '', telefone)
            
            existing_user = get_object_or_404(Cadastro, username=nome)

            # Atualize as informações existentes
            existing_user.email = email
            existing_user.first_name = nome
            existing_user.last_name = sobrenome
            existing_user.code_area = ddd
            existing_user.phone = telefone_limpo
            existing_user.type_document = documento
            existing_user.cpf_cnpj = num_documento
            existing_user.date_birthday = nascimento
            existing_user.cep = cep
            existing_user.endereco = endereco
            existing_user.complemento = complemento
            existing_user.number = numero
            existing_user.bairro = bairro

            # Salve as alterações no banco de dados
            existing_user.save()
            messages.success(request, "Cadastrado atualizado com sucesso!", extra_tags="success")
            return redirect(reverse('dados_pessoais'))
    return render(request, "ecommerce_main/e-dados_pessoais.html", {"dados": request.user})

@login_required_message_and_redirect(login_url='login_view')
def change_password(request):
    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Atualiza a sessão para que o usuário não precise fazer login novamente
            messages.success(request, "Senha Alterado com sucesso!", extra_tags="success")
            return redirect('change_password')
    else:
        form = SetPasswordForm(request.user)
    return render(request, "ecommerce_main/e-dados_pessoais.html", {'form_senha': form})

@login_required_message_and_redirect(login_url='login_view')
def historico_compras(request):
    try:
        user = Cadastro.objects.get(pk=request.user.id)
        pagamentos = Payments.objects.filter(user=user).order_by('-date_created')
    except Cadastro.DoesNotExist:
        pagamentos = "usuario não existente"
        pass
    except Payments.DoesNotExist:
        pagamentos = "nenhum registro de compras"
        pass
    return render(request, "ecommerce_main/e-dados_pessoais.html", {"pagamentos": pagamentos})

@login_required_message_and_redirect(login_url='login_view')
def prod_historico_compra(request, id_payment):
    try:
        history = Payments.objects.filter(id_payment=id_payment).first()
        prod = history.products
    except Payments.DoesNotExist:
        history = "Não encontrado nenhum produto com esse ID"
    return render(request, "ecommerce_main/e-historico_produto.html", {"history": history, "prods": prod})