from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models

class Cadastro(AbstractUser):

    is_colaborador = models.BooleanField(default=False)

    DOCUMENTO_CHOICES = (
        ('cpf', 'CPF'),
        ('cnpj', 'CNPJ'),
    )

    email = models.EmailField(_("endereço de e-mail"),max_length=100, unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    date_birthday = models.DateTimeField(null=True, blank=True)
    cep = models.CharField(max_length=10,null=True, blank=True)
    bairro = models.CharField(max_length=50, null=True, blank=True)
    endereco = models.CharField(max_length=100, null=True, blank=True)
    number = models.CharField(max_length=8, null=True, blank=True)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    code_area = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    type_document = models.CharField(max_length=5, choices=DOCUMENTO_CHOICES, null=True, blank=True)
    cpf_cnpj = models.CharField(max_length=20,null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'cadastro'
    
    def __str__(self):
        return self.email
    
