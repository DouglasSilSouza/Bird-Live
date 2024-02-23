from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.db import models
from django.utils import timezone

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
    activation_token = models.CharField(max_length=32, blank=True, null=True)
    activation_token_created_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    slug = models.SlugField(unique=True,null=True, blank=True, allow_unicode=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    class Meta:
        db_table = 'cadastro'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_activation_token_valid(self):
        if self.activation_token_created_at:
            expiration_time = self.activation_token_created_at + timezone.timedelta(minutes=15)
            return timezone.now() <= expiration_time
        return False
    
    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(f"{self.first_name} {self.last_name}")
        return super().save(*args, **kwargs)
