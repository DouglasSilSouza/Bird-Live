from django.shortcuts import render
from app_authentication.models import Cadastro
from app_payment.models import Payments
from ecommerce_cart.models import ItemCarrinho
from django.db.models import Sum

# Create your views here.
def home(request):
    user = Cadastro.objects.count()
    pays = Payments.objects.aggregate(soma=Sum('interest_free_value'))['soma']
    context = {
        "users": user,
        "pays": pays
    }
    return render(request, 'app_main/inicio.html', context=context)

def admin_carts(request):
    pays = Payments.objects.all()

    context = {
        "pays": pays
    }
    return render(request, "app_main/admin_payments.html", context=context)

def admin_payments(request, id):
    pay = Payments.objects.get(pk=id)

    context = {
        "pay": pay
    }
    return render(request, "app_main/admin_payment.html", context=context)

def usuarios(request):
    users = Cadastro.objects.all()
    return render(request, "app_main/usuarios.html", {"users": users})

def only_usuario(request, id):
    user = Cadastro.objects.get(pk=id)
    return render(request, "app_main/only_usuario.html", {"user": user})